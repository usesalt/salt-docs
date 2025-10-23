"""
Mermaid Diagram Formatter Utility

This utility provides functions to properly format Mermaid diagrams
to avoid common syntax issues that prevent rendering.
"""

import re
from typing import List, Dict, Any


def clean_node_labels(text: str) -> str:
    """
    Clean node labels by removing line breaks and ensuring proper quoting.
    
    Args:
        text: Raw text that may contain line breaks in node labels
        
    Returns:
        Cleaned text with proper Mermaid syntax
    """
    # Fix node labels with line breaks inside quotes
    # Pattern: ["text with\nline break"] -> ["text with line break"]
    pattern = r'\["([^"]*?)\n([^"]*?)"\]'
    replacement = r'["\1 \2"]'
    text = re.sub(pattern, replacement, text)
    
    # Remove any remaining line breaks in node labels
    pattern = r'\["([^"]*?)\n([^"]*?)"\]'
    while re.search(pattern, text):
        text = re.sub(pattern, r'["\1 \2"]', text)
    
    return text


def format_flowchart(nodes: List[Dict[str, Any]], connections: List[Dict[str, str]]) -> str:
    """
    Generate a properly formatted Mermaid flowchart.
    
    Args:
        nodes: List of node definitions with id, label, and type
        connections: List of connections with from, to, and label
        
    Returns:
        Formatted Mermaid flowchart string
    """
    mermaid = ["flowchart TD"]
    
    # Add nodes
    for node in nodes:
        node_id = node["id"]
        label = node["label"].replace("\n", " ").strip()
        node_type = node.get("type", "default")
        
        if node_type == "start":
            mermaid.append(f'    {node_id}["{label}"]')
        elif node_type == "end":
            mermaid.append(f'    {node_id}["{label}"]')
        elif node_type == "process":
            mermaid.append(f'    {node_id}("{label}")')
        elif node_type == "decision":
            mermaid.append(f'    {node_id}{{{label}}}')
        else:
            mermaid.append(f'    {node_id}["{label}"]')
    
    # Add connections
    for conn in connections:
        from_node = conn["from"]
        to_node = conn["to"]
        label = conn.get("label", "")
        
        if label:
            mermaid.append(f'    {from_node} -- "{label}" --> {to_node}')
        else:
            mermaid.append(f'    {from_node} --> {to_node}')
    
    return "\n".join(mermaid)


def format_sequence_diagram(participants: List[Dict[str, str]], interactions: List[Dict[str, str]]) -> str:
    """
    Generate a properly formatted Mermaid sequence diagram.
    
    Args:
        participants: List of participants with id and label
        interactions: List of interactions with from, to, and message
        
    Returns:
        Formatted Mermaid sequence diagram string
    """
    mermaid = ["sequenceDiagram"]
    
    # Add participants
    for participant in participants:
        participant_id = participant["id"]
        label = participant["label"].replace("\n", " ").strip()
        mermaid.append(f'    participant {participant_id} as {label}')
    
    # Add interactions
    for interaction in interactions:
        from_participant = interaction["from"]
        to_participant = interaction["to"]
        message = interaction["message"]
        arrow_type = interaction.get("arrow", "->")
        
        mermaid.append(f'    {from_participant}{arrow_type}{to_participant}: {message}')
    
    return "\n".join(mermaid)


def format_class_diagram(classes: List[Dict[str, Any]]) -> str:
    """
    Generate a properly formatted Mermaid class diagram.
    
    Args:
        classes: List of class definitions with name, attributes, and methods
        
    Returns:
        Formatted Mermaid class diagram string
    """
    mermaid = ["classDiagram"]
    
    for class_def in classes:
        class_name = class_def["name"]
        mermaid.append(f'    class {class_name} {{')
        
        # Add attributes
        for attr in class_def.get("attributes", []):
            visibility = attr.get("visibility", "+")
            attr_name = attr["name"]
            attr_type = attr.get("type", "")
            mermaid.append(f'        {visibility}{attr_name}: {attr_type}')
        
        # Add methods
        for method in class_def.get("methods", []):
            visibility = method.get("visibility", "+")
            method_name = method["name"]
            method_params = method.get("params", "")
            method_return = method.get("return", "")
            mermaid.append(f'        {visibility}{method_name}({method_params}): {method_return}')
        
        mermaid.append("    }")
    
    return "\n".join(mermaid)


def validate_mermaid_syntax(mermaid_text: str) -> List[str]:
    """
    Validate Mermaid syntax and return list of errors.
    
    Args:
        mermaid_text: Mermaid diagram text to validate
        
    Returns:
        List of error messages
    """
    errors = []
    
    # Check for common issues
    if "```mermaid" in mermaid_text and "```" not in mermaid_text.split("```mermaid")[1]:
        errors.append("Missing closing ``` for mermaid block")
    
    # Check for line breaks in node labels
    if re.search(r'\["[^"]*?\n[^"]*?"\]', mermaid_text):
        errors.append("Line breaks found in node labels - use spaces instead")
    
    # Check for incomplete sequence diagrams
    if "sequenceDiagram" in mermaid_text:
        lines = mermaid_text.split('\n')
        participant_count = sum(1 for line in lines if line.strip().startswith('participant'))
        interaction_count = sum(1 for line in lines if '->>' in line or '->' in line)
        
        if participant_count > 0 and interaction_count == 0:
            errors.append("Sequence diagram has participants but no interactions")
    
    return errors


def fix_common_issues(mermaid_text: str) -> str:
    """
    Fix common Mermaid syntax issues.
    
    Args:
        mermaid_text: Raw Mermaid text with potential issues
        
    Returns:
        Fixed Mermaid text
    """
    # Remove mermaid code block markers if present
    text = mermaid_text.replace("```mermaid\n", "").replace("```", "")
    
    # Fix line breaks in node labels
    text = clean_node_labels(text)
    
    # Fix generic type syntax in class diagrams
    text = re.sub(r'List~([^~]+)~', r'List<\1>', text)
    
    # Ensure proper line endings
    text = text.strip()
    
    return text


# Example usage and testing
if __name__ == "__main__":
    # Test the formatter
    test_flowchart = """
    flowchart TD
        A["SAP Order Processing Pipeline
    "]
        B["SFTP Batch Upload Job
    "]
        A --> B
    """
    
    fixed = fix_common_issues(test_flowchart)
    print("Fixed flowchart:")
    print(fixed)
    
    # Test validation
    errors = validate_mermaid_syntax(test_flowchart)
    if errors:
        print("Errors found:", errors)
    else:
        print("No syntax errors found")
