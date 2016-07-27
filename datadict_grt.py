# WB Datadict - MySQL Workbench plugin to generate data dictionaries.
#
# Public domain 2011 sirgazil. All rights waived.

import os
import datetime
import webbrowser

from wb import *
import grt
import mforms as gui


# PLUGIN
# ======

ModuleInfo = DefineModule(name="WB Datadict",
                          author="sirgazil",
                          version="1.1.0")
@ModuleInfo.plugin("my.plugin.create_datadict",
                   caption="Generate HTML Data Dictionary",
                   input=[wbinputs.currentCatalog()],
                   pluginMenu="Catalog")
@ModuleInfo.export(grt.INT, grt.classes.db_Catalog)


def create_datadict(catalog):
    # Get default schema
    schema = catalog.defaultSchema

    # Get table objects and sort them alphabetically
    tables = sorted(schema.tables, key=lambda table: table.name)

    # Add header to the markup and replace header variables
    markup = get_header()
    markup = markup.replace("[PROJECTNAME]", schema.name)
    markup = markup.replace("[DESCRIPTION]", escape(schema.comment))
    markup = markup.replace("[EDITION]", str(datetime.date.today()))

    # Add alphabetic index links
    markup += "<h2>Alphabetic Index</h2>\n"
    markup += "<ul>\n"
    for table in tables:
        markup += "<li><a href='#{0}'>{0}</a></li>\n".format(table.name)
    markup += "</ul>\n"

    # Format table objects in HTML
    for table in tables:
        markup += "<table id='{0}'>\n".format(table.name)
        markup += "<caption>{0}</caption>\n".format(table.name)
        markup += "<tr><td colspan='12'>{0}</td></tr>\n".format(escape(table.comment))
        markup += get_colnames()

        # Format column objects in HTML
        for column in table.columns:
            markup += "<tr>\n"
            markup += "    <td class='field'>{0}</td>\n".format(column.name)
            markup += "    <td>{0}</td>\n".format(column.formattedType)

            # Check for Primary Key
            if table.isPrimaryKeyColumn(column):
                markup += "    <td class='centered'>&#10004;</td>\n"
            else:
                markup += "    <td class='centered'>&nbsp;</td>\n"

            # Check for Foreign Key
            if table.isForeignKeyColumn(column):
                markup += "    <td class='centered'><a href='#{0}'>&#10004;</a></td>\n".format(column.name.replace("_id", ""))
            else:
                markup += "    <td class='centered'>&nbsp;</td>\n"

            # Check for Not Null attribute
            if column.isNotNull == 1:
                markup += "    <td class='centered'>&#10004;</td>\n"
            else:
                markup += "    <td class='centered'>&nbsp;</td>\n"

            # Check for Unique attribute
            if is_unique(column, table):
                markup += "    <td class='centered'>&#10004;</td>\n"
            else:
                markup += "    <td class='centered'>&nbsp;</td>\n"

            # Check for Binary, Unsigned and Zero Fill attributes
            flags = list(column.flags)

            if flags.count("BINARY"):
                markup += "    <td class='centered'>&#10004;</td>\n"
            else:
                markup += "    <td class='centered'>&nbsp;</td>\n"

            if flags.count("UNSIGNED"):
                markup += "    <td class='centered'>&#10004;</td>\n"
            else:
                markup += "    <td class='centered'>&nbsp;</td>\n"

            if flags.count("ZEROFILL"):
                markup += "    <td class='centered'>&#10004;</td>\n"
            else:
                markup += "    <td class='centered'>&nbsp;</td>\n"

            # Check for Auto Increment attribute
            if column.autoIncrement == 1:
                markup += "    <td class='centered'>&#10004;</td>\n"
            else:
                markup += "    <td class='centered'>&nbsp;</td>\n"

            # Add Default value
            dv = column.defaultValue
            markup += "    <td>{0}</td>\n".format(dv)


            markup += "    <td>{0}</td>\n".format(escape(column.comment))
            markup += "</tr>\n"

        markup += "</table>\n"

    # Add footer to the markup
    markup += get_footer()

    # Write the HTML file to disk
    doc_path = os.path.dirname(grt.root.wb.docPath)

    dialog = gui.FileChooser(gui.SaveFile)
    dialog.set_title("Save HTML data dictionary")
    dialog.set_directory(doc_path)
    response = dialog.run_modal()
    file_path = dialog.get_path()

    if response:
        try:
            html_file = open(file_path, "w")
        except IOError:
            text = "Could not open {0}.".format(file_path)
            gui.Utilities.show_error("Error saving the file", text, "Ok",
                                       "", "")
        else:
            html_file.write(markup)
            html_file.close()

            title = "{0}'s data dictionary".format(schema.name)
            text = "The data dictionary was successfully generated."
            gui.Utilities.show_message(title, text, "Ok", "", "")

            # Open HTML file in the Web browser
            try:
                webbrowser.open_new(file_path)
            except webbrowser.Error:
                print("Warning: Could not open the data dictionary in " +
                      "the Web browser.")

    return 0



# HELPER FUNCTIONS
# ================

def escape(text):
    """Return text as an HTML-safe sequence."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&apos;")
    return text


def get_header():
    """Return the top part of the HTML document."""
    header = """<!DOCTYPE html>\n\
<html lang="en">\n\
<head>\n\
    <meta charset="UTF-8">\n\
    <meta name="author" content="WB Datadict">\n\
    <meta name="description" content="[PROJECTNAME] Data Dictionary.">\n\
    <title>[PROJECTNAME] Data Dictionary</title>\n\
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>\n\
    <script>
      // Highlight table corresponding to the current fragment in the URL.
      $(document).ready(function(){
        $("a").click(function() {
          var elem = $(this);
          // Remove all classes from tables.
          $("table").removeClass( "focused" )
          // Get a.href value and extract its fragment id.
          var id = elem.attr("href");
          // Highlight table using fragment id.
          $(id).addClass( "focused" );
        });
      });
    </script>
    <style type="text/css">\n\
    a{\n\
        text-decoration: none;\n\
    }\n\
    abbr{\n\
        cursor: help;\n\
    }\n\
    header{\n\
        color: #6A6A6A;\n\
        text-align: right;\n\
    }\n\
    table{\n\
        border-collapse: collapse;\n\
        margin-bottom: 30px;\n\
        width: 100%;\n\
    }\n\
    table caption{\n\
        font-size: 120%;\n\
        font-weight: bold;\n\
    }\n\
    table, td, th{\n\
        border-color: silver;\n\
        border-style: solid;\n\
        border-width: 1px;\n\
    }\n\
    caption{\n\
        color: black;\n\
    }\n\
    td, th{\n\
        padding: 1em;\n\
    }\n\
    tr:hover{\n\
        color: #333;\n\
        background-color: #F2F2F2;\n\
    }\n\
    th{\n\
        background-color: #F5F5F5;\n\
    }\n\
    td{\n\
        color: #6A6A6A;\n\
    }\n\
    ul{\n\
        font-style: italic;\n\
    }\n\
    .centered{\n\
        text-align: center;\n\
    }\n\
    .field{\n\
        color: #4C4C4C;\n\
        font-weight: bold;\n\
    }\n\
    .focused{\n\
        outline-color: aqua;\n\
        outline-style: solid;\n\
        outline-width: thin;\n\
    }\n\
    </style>\n\
</head>\n\
<body>\n\
<header>\n\
<h1>[PROJECTNAME]<br> Data Dictionary</h1>\n\
<p>\n\
<em>[EDITION]</em>\n\
</p>\n\
<p>\n\
<em>[DESCRIPTION]</em>\n\
</p>\n\
</header>\n\
"""
    return header


def get_colnames():
    """Return HTML row with header cells used in all tables."""
    colnames = ("<tr>\n" +
                "    <th>Column name</th>\n" +
                "    <th>DataType</th>\n" +
                "    <th><abbr title='Primary Key'>PK</abbr></th>\n" +
                "    <th><abbr title='Foreign Key'>FK</abbr></th>\n" +
                "    <th><abbr title='Not Null'>NN</abbr></th>\n" +
                "    <th><abbr title='Unique'>UQ</abbr></th>\n" +
                "    <th><abbr title='Binary'>BIN</abbr></th>\n" +
                "    <th><abbr title='Unsigned'>UN</abbr></th>\n" +
                "    <th><abbr title='Zero Fill'>ZF</abbr></th>\n" +
                "    <th><abbr title='Auto Increment'>AI</abbr></th>\n" +
                "    <th>Default</th>\n" +
                "    <th>Comment</th>\n" +
                "</tr>\n")
    return colnames


def get_footer():
    """Return the bottom part of the HTML document."""
    return "</body>\n</html>"


def is_unique(column, table):
    """Return true if the column is UNIQUE."""
    result = False

    for index in table.indices:
        if index.name == "{0}_UNIQUE".format(column.name):
            result = True
            break

    return result
