from google import genai
from google.genai import types
import dotenv
import logging
import re
import ast
import json
import os
from typing import List


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


dotenv.load_dotenv() 
client = genai.Client()

search_tool = types.Tool(
    google_search=types.GoogleSearch()
)

USE_GROUNDING = True


def parse_list_from_response(response_text: str) -> List[str]:
    list_pattern = r'\[.*?\]'
    match = re.search(list_pattern, response_text, re.DOTALL)
    
    if match:
        try:
          
            return ast.literal_eval(match.group(0))
        except:  
            try:
            
                fixed = match.group(0).replace("'", "\"")
                return json.loads(fixed)
            except:
                print(f"Couldn't parse: {response_text}")
    
    matches = re.findall(r'[\'"]([a-zA-Z0-9_-]+)[\'"]', response_text)
    
    return matches if matches else []


def github_name_extractor(pdf_text: str) -> List[str]:
    if not pdf_text or pdf_text.strip() == "":
        print("Warning: Empty PDF text!")
        return []
    
    try:
        max_chars = 10000  
        trimmed_text = pdf_text[:max_chars]
        
        prompt = (
            "Extract all GitHub organization usernames of tech companies mentioned in this text. "
            "For example, if you see 'github.com/microsoft' or 'Microsoft's GitHub (microsoft)', "
            "extract 'microsoft'. Include both explicit mentions and implied GitHub handles. "
            "Return ONLY a Python list of lowercase usernames without explanation. "
            "Example response: ['google', 'microsoft', 'facebook']\n\n"
            f"{trimmed_text}"
        )
        
        config = types.GenerateContentConfig(
            tools=[search_tool]
        )
        
        print("Extracting GitHub usernames...")
        response = client.models.generate_content(
            model="gemini-2.5-pro",  
            contents=prompt,
            config=config if USE_GROUNDING else None
        )
        
        if response and response.text:
            usernames = parse_list_from_response(response.text)
            
            clean_usernames = []
            for name in usernames:
                clean_name = name.replace('github.com/', '')
                clean_name = clean_name.strip().lower()
                
                if clean_name:
                    clean_usernames.append(clean_name)
            
            print(f"Found {len(clean_usernames)} GitHub usernames: {clean_usernames}")
            return clean_usernames
        else:
            print("No response from API :(")
            return []
        
    except Exception as e:
        print(f"Error extracting GitHub usernames: {str(e)}")
        return []
        
        
def extract_github_metadata(usernames: List[str]) -> List[dict]:
   
    if not usernames:
        return []
        
    all_results = []
    
    config = None
    if USE_GROUNDING:
        config = types.GenerateContentConfig(
            tools=[search_tool]
        )
    
    for username in usernames:
        if not username or username.strip() == "":
            continue
            
        try:
           
            prompt = (
                f"Tell me about GitHub org '{username}'. "
                "Format as JSON with these fields: "
                "{username, full_name, description, website, industry, employee_count}"
            )
            
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config
            )
            
            if response and response.text:
            
                try:
                    
                    json_pattern = r'\{.*\}'
                    match = re.search(json_pattern, response.text, re.DOTALL)
                    
                    if match:
                        
                        json_str = match.group(0).replace("'", "\"")
                        data = json.loads(json_str)
                        all_results.append(data)
                        print(f"Found info for {username}")
                    else:
                        all_results.append({"username": username})
                except Exception as e:
                    print(f"Error parsing JSON for {username}: {str(e)}")
                    all_results.append({"username": username})
        except Exception as e:
            print(f"API error for {username}: {str(e)}")
            all_results.append({"username": username})
    
    return all_results
