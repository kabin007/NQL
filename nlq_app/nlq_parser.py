from groq import Groq

client = Groq()  

def parse_to_sql(user_query):
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": f"translate this into sql statement {user_query} dont output any texts besides query"
            },
            {
                "role": "user",
                "content": ""
            },
            {
                "role": "assistant",
                "content": ""
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=[";"],
    )

    response_content = ""
    for chunk in response:
        chunk_content = chunk.choices[0].delta.content or ""
        response_content += chunk_content
    
    response_content=response_content+";"
   
    
    
    return response_content

