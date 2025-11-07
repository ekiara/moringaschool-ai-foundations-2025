import csv
import os
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
from pathlib import Path


def validate_csv_schema(
    file_path: str,
    schema: Dict[str, Dict[str, Any]],
    encoding: str = 'utf-8',
    delimiter: str = ',',
    max_errors: Optional[int] = None
) -> Dict[str, Any]:
    """
    Validates a CSV file against a defined schema.
    
    Args:
        file_path: Path to the CSV file to validate
        schema: Dictionary defining the expected structure. Format:
            {
                'column_name': {
                    'type': str|int|float|bool|datetime,  # Expected data type
                    'required': True|False,                # Whether nulls are allowed
                    'validator': callable,                 # Optional custom validation function
                    'nullable': True|False                 # Alternative to 'required'
                }
            }
        encoding: File encoding (default: 'utf-8')
        delimiter: CSV delimiter (default: ',')
        max_errors: Maximum number of errors to collect before stopping (default: None = all)
    
    Returns:
        Dictionary with validation results:
        {
            'valid': bool,
            'file_path': str,
            'total_rows': int,
            'rows_validated': int,
            'error_count': int,
            'summary': {
                'file_errors': int,
                'structural_errors': int,
                'type_errors': int,
                'required_errors': int,
                'custom_errors': int
            },
            'errors': [
                {
                    'line': int,
                    'column': str,
                    'error_type': str,
                    'message': str,
                    'value': any
                }
            ]
        }
    
    Example:
        schema = {
            'user_id': {'type': int, 'required': True},
            'email': {'type': str, 'required': True},
            'age': {'type': int, 'required': False},
            'signup_date': {'type': datetime, 'required': True}
        }
        result = validate_csv_schema('users.csv', schema)
    """
    
    # Initialize result dictionary
    result = {
        'valid': True,
        'file_path': file_path,
        'total_rows': 0,
        'rows_validated': 0,
        'error_count': 0,
        'summary': {
            'file_errors': 0,
            'structural_errors': 0,
            'type_errors': 0,
            'required_errors': 0,
            'custom_errors': 0
        },
        'errors': []
    }
    
    def add_error(line: int, column: str, error_type: str, message: str, value: Any = None):
        """Helper function to add an error to the result."""
        result['errors'].append({
            'line': line,
            'column': column,
            'error_type': error_type,
            'message': message,
            'value': value
        })
        result['error_count'] += 1
        result['summary'][f'{error_type}_errors'] += 1
        result['valid'] = False
    
    # Check if max_errors limit reached
    def should_continue():
        return max_errors is None or result['error_count'] < max_errors
    
    # File Access Validation
    try:
        if not os.path.exists(file_path):
            add_error(0, '', 'file', f"File not found: {file_path}")
            return result
        
        if not os.path.isfile(file_path):
            add_error(0, '', 'file', f"Path is not a file: {file_path}")
            return result
        
        if os.path.getsize(file_path) == 0:
            add_error(0, '', 'file', "File is empty")
            return result
            
    except Exception as e:
        add_error(0, '', 'file', f"File access error: {str(e)}")
        return result
    
    # Encoding Validation
    try:
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            # Try to read first line to validate encoding
            f.readline()
    except UnicodeDecodeError as e:
        add_error(0, '', 'file', f"Encoding error: Unable to read file with {encoding} encoding. {str(e)}")
        return result
    except Exception as e:
        add_error(0, '', 'file', f"Error opening file: {str(e)}")
        return result
    
    # CSV Structure and Data Validation
    try:
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            
            # Validate CSV headers
            if reader.fieldnames is None:
                add_error(1, '', 'structural', "No headers found in CSV file")
                return result
            
            csv_columns = set(reader.fieldnames)
            schema_columns = set(schema.keys())
            
            # Check for missing required columns
            missing_columns = schema_columns - csv_columns
            if missing_columns:
                for col in missing_columns:
                    add_error(1, col, 'structural', f"Required column '{col}' not found in CSV headers")
            
            # Check for unexpected columns (warning, not error)
            extra_columns = csv_columns - schema_columns
            
            # If structural errors exist, return early
            if result['summary']['structural_errors'] > 0:
                return result
            
            # Validate each row
            for line_num, row in enumerate(reader, start=2):  # Start at 2 (header is line 1)
                if not should_continue():
                    break
                
                result['total_rows'] += 1
                row_valid = True
                
                # Check each column in schema
                for column, rules in schema.items():
                    value = row.get(column, '').strip()
                    
                    # Check if value is empty
                    is_empty = value == '' or value is None
                    
                    # Required/Nullable check
                    required = rules.get('required', not rules.get('nullable', True))
                    if required and is_empty:
                        add_error(line_num, column, 'required', 
                                f"Required field '{column}' is empty or missing")
                        row_valid = False
                        if not should_continue():
                            break
                        continue
                    
                    # Skip type checking if value is empty and field is nullable
                    if is_empty:
                        continue
                    
                    # Type validation
                    expected_type = rules.get('type')
                    if expected_type:
                        try:
                            if expected_type == int:
                                int(value)
                            elif expected_type == float:
                                float(value)
                            elif expected_type == bool:
                                if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                                    raise ValueError("Invalid boolean value")
                            elif expected_type == datetime:
                                # Try common date formats
                                parsed = False
                                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y', '%d/%m/%Y']:
                                    try:
                                        datetime.strptime(value, fmt)
                                        parsed = True
                                        break
                                    except ValueError:
                                        continue
                                if not parsed:
                                    raise ValueError("Invalid date format")
                            elif expected_type == str:
                                # String type always valid for non-empty values
                                pass
                        except (ValueError, TypeError) as e:
                            add_error(line_num, column, 'type',
                                    f"Invalid type for '{column}'. Expected {expected_type.__name__}, got '{value}'",
                                    value)
                            row_valid = False
                            if not should_continue():
                                break
                            continue
                    
                    # Custom validator
                    custom_validator = rules.get('validator')
                    if custom_validator and callable(custom_validator):
                        try:
                            if not custom_validator(value):
                                add_error(line_num, column, 'custom',
                                        f"Custom validation failed for '{column}' with value '{value}'",
                                        value)
                                row_valid = False
                        except Exception as e:
                            add_error(line_num, column, 'custom',
                                    f"Custom validator error for '{column}': {str(e)}",
                                    value)
                            row_valid = False
                        
                        if not should_continue():
                            break
                
                if row_valid:
                    result['rows_validated'] += 1
    
    except csv.Error as e:
        add_error(0, '', 'structural', f"CSV parsing error: {str(e)}")
    except Exception as e:
        add_error(0, '', 'file', f"Unexpected error during validation: {str(e)}")
    
    return result


def print_validation_report(result: Dict[str, Any], verbose: bool = False):
    """
    Pretty-prints the validation result.
    
    Args:
        result: The result dictionary from validate_csv_schema
        verbose: If True, prints all errors. If False, prints summary only.
    """
    print("\n" + "="*70)
    print("CSV VALIDATION REPORT")
    print("="*70)
    print(f"File: {result['file_path']}")
    print(f"Status: {'✓ VALID' if result['valid'] else '✗ INVALID'}")
    print(f"Total Rows: {result['total_rows']}")
    print(f"Rows Validated: {result['rows_validated']}")
    print(f"Total Errors: {result['error_count']}")
    
    if result['error_count'] > 0:
        print("\n" + "-"*70)
        print("ERROR SUMMARY")
        print("-"*70)
        for error_type, count in result['summary'].items():
            if count > 0:
                print(f"{error_type.replace('_', ' ').title()}: {count}")
        
        if verbose and result['errors']:
            print("\n" + "-"*70)
            print("DETAILED ERRORS")
            print("-"*70)
            for i, error in enumerate(result['errors'][:100], 1):  # Limit to first 100
                print(f"\n{i}. Line {error['line']}, Column '{error['column']}'")
                print(f"   Type: {error['error_type']}")
                print(f"   Message: {error['message']}")
                if error['value'] is not None:
                    print(f"   Value: {error['value']}")
            
            if len(result['errors']) > 100:
                print(f"\n... and {len(result['errors']) - 100} more errors")
    
    print("\n" + "="*70 + "\n")


# Example usage
if __name__ == "__main__":
    # Define schema
    schema = {
        'user_id': {'type': int, 'required': True},
        'username': {'type': str, 'required': True},
        'email': {'type': str, 'required': True},
        'age': {'type': int, 'required': False},
        'signup_date': {'type': datetime, 'required': True},
        'is_active': {'type': bool, 'required': False}
    }
    
    # Validate CSV
    result = validate_csv_schema('users.csv', schema)
    
    # Print report
    print_validation_report(result, verbose=True)
