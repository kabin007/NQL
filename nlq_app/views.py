from django.shortcuts import render
from django.db import connection
from . import nlq_parser
import re

# Create your views here.
def home(request):
    context={
        "message":"",
        "table_columns":None,
        "table_data":None,
        "statement":"",
        "table_name":""
    }

    if request.method == "POST":
        user_prompt = request.POST.get('prompt')
        sql_statement = nlq_parser.parse_to_sql(user_prompt)
        context["statement"]=sql_statement
        

        print(sql_statement)
        
        try:
            with connection.cursor() as cursor:
                sql_type=sql_statement.split()[0].upper()

                if sql_type in ["SELECT"]:
                    cursor.execute(sql_statement)
                    context["table_data"]=cursor.fetchall()
                    context["table_columns"]=[disc[0] for disc in  cursor.description]
                    context["message"]="Query executed successfully, Data retreived"
                    context["table_name"]=extract_table_name(sql_statement)

                elif sql_type in ["UPDATE","DELETE"]:
                    cursor.execute(sql_statement)
                    connection.commit()
                    affected_rows=cursor.rowcount()
                    context["message"]=f"{affected_rows} affected by the statement {sql_statement}"
                    context["table_name"]=extract_table_name(sql_statement)
                    context["table_data"]=cursor.fetchall()
                    context["table_columns"]=[disc[0] for disc in  cursor.description]
               
                elif sql_type in ["CREATE","DROP"]:
                    cursor.execute(sql_statement)
                    connection.commit()
                    context["message"]=f"Table opreation {sql_type.lower()} executed successfully"
                    context["table_name"]=extract_table_name(sql_statement)
                    context["table_columns"]=[disc[0] for disc in  cursor.description]
                else:
                    cursor.execute(sql_statement)
                    connection.commit()
                    context["message"]="Query executed successfully"
                    context["table_name"]=extract_table_name(sql_statement)
                    context["table_columns"]=[disc[0] for disc in  cursor.description]
        
        except Exception as e:
            context["message"]=f"An error occurred: {e}"
    

    return render(request,'index.html',context)


def extract_table_name(sql_statement):
    if sql_statement.upper().startswith("SELECT"):
        match = re.search(r"FROM\s+(\w+)", sql_statement, re.IGNORECASE)

    elif sql_statement.upper().startswith(("CREATE", "DROP")):
        match = re.search(r"(CREATE|DROP)\s+TABLE\s+(\w+)", sql_statement, re.IGNORECASE)

    elif sql_statement.startswith("UPDATE"):
        match = re.search(r"UPDATE\s+(\w+)", sql_statement, re.IGNORECASE)
        if match:
            return match.group(1)
    
    else:
        match = None

    if match:
        return match.group(1 if sql_statement.upper().startswith("SELECT") else 2)
    else:
        return None