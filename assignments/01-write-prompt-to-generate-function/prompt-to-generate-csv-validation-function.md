# 🤖 Project: Prompt to generate a CSV Validation Function

---

## 🎯 **Description**

I decided to do a prompt to generate a function similar to something we already use at my workplace. I get a lot of data from external sources and it is often in CSV format. The CSVs are occsionally not formatted correctly, or missing fields or they have other issues that need to be dealt with before the data can be used. A first step in dealing with these CSVs is to validate that they are in the correct format.

---

## 🎯 **The Prompt**

I need you to write a Python function called validate_csv_schema. Its main job is to act as a data quality gatekeeper, checking if a CSV file matches a defined schema before the data is processed further. The function should read the file, check each row against the schema rules, and collect any errors it finds into a detailed report.

The two most critical things to check for are basic file access issues, like the file not existing or having encoding problems, and structural problems with the CSV itself, such as missing headers or columns that don't match the schema. For the data inside, the most important checks are for incorrect data types, like text in a number field, and missing values in columns that are marked as required.

Please make the function robust and return a clear dictionary report showing if the file is valid, a summary of the issues found, and a list of all violations with line numbers and descriptions. It should handle large files efficiently and provide useful error messages.

