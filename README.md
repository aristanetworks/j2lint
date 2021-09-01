# Jinja2-Linter

AVD Ecosystem - Jinja2 Linter

The goal of this project is to build a Jinja2 linter that will provide the following capabilities:

- Validate syntax according to AVD style guide: https://avd.sh/en/latest/docs/contribution/style-guide.html
- Develop extension that works with VSCode and potentianly others IDEs i.e PyCharm
  - if supporting multiple IDEs adds to much complexity, support for VSCode will take priority
- Capability to run as a GitHub Action and used to enforce style in our CI pipeline


Syntax and code style issues detected by Jinja2 Linter are:
1. SYNTAX-0 Jinja2 syntax should be correct
2. SYNTAX-1 A single space shall be added between Jinja2 curly brackets and a variable’s name
3. SYNTAX-2 When variables are used in combination with a filter, | shall be enclosed by space
4. SYNTAX-3 Nested jinja code block shall follow next rules:
   - All J2 statements must be enclosed by 1 space
   - All J2 statements must be indented by 4 more spaces within jinja delimiter
   - To close a control, end tag must have same indentation level
   - Indentation are 4 spaces and NOT tabulation
5. SYNTAX-7 Jinja statements should be on separate lines
6. VAR-1 All variables shall use lower case
7. VAR-2 If variable is multi-words, underscore _ shall be used as a separator
