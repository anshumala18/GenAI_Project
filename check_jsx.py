
import sys

def check_balance(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple brace counter
    braces = 0
    parens = 0
    cur_line = 1
    
    for char in content:
        if char == '{': braces += 1
        elif char == '}': braces -= 1
        elif char == '(': parens += 1
        elif char == ')': parens -= 1
        
    print(f"Braces balance: {braces}")
    print(f"Parens balance: {parens}")

    # Simplified JSX tag counter (only looks for <TagName and </TagName)
    # This is rough but can catch obvious mismatches
    import re
    tags = re.findall(r'<([a-zA-Z0-9\.]+)', content)
    closed_tags = re.findall(r'</([a-zA-Z0-9\.]+)', content)
    
    print(f"Opening tags found: {len(tags)}")
    print(f"Closing tags found: {len(closed_tags)}")
    
    tag_counts = {}
    for t in tags: tag_counts[t] = tag_counts.get(t, 0) + 1
    for t in closed_tags: tag_counts[t] = tag_counts.get(t, 0) - 1
    
    mismatches = {k: v for k, v in tag_counts.items() if v != 0}
    # Filter out self-closing tags like <input />, <Loader2 />, etc.
    # Note: this script isn't perfect for self-closing but helps
    print(f"Potential tag mismatches (excluding self-closing): {mismatches}")

if __name__ == "__main__":
    check_balance(sys.argv[1])
