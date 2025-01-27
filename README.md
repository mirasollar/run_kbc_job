# Upload and Edit Tables
This Data App eliminates the need to export data to external tools, allowing business users to directly access and edit tables stored in Keboola Storage. By centralizing data editing, it enhances collaboration, reduces errors, and streamlines your data management processes. Experience a more efficient and accessible way to edit and manage data with this app.
The app can check data integrity. It's possible to set the primary key, set data types for individual columns and require non-empty values. The primary key checks the uniqueness of the data, with the default being case insensitive. Each column of type string can be set as case sensitive. The uniqueness of the data is also checked at the whole row level.
The primary key setting is taken from the table settings in the primary key section. The column settings are taken from the table description and must be in this format:

Upload setting:` ```{'column_name_1': 'data type, setting empty rows', 'column_name_2': 'data type, setting empty rows'}``` `

Possible settings of data types: string, number, logical, date with percentage mark, for example %Y-%m-%d. The [strftime]([https://duckduckgo.com](https://strftime.org/) module is used to check the date format.
