def build_structure_prompt(file_tree: str, readme: str, owner: str, repo: str, language: str = "en", comprehensive: bool = True) -> str:
    """
    Build the XML wiki structure generation prompt.
    """
    language_map = {
        "en": "English",
        "ja": "Japanese (日本語)",
        "zh": "Mandarin Chinese (中文)",
        "zh-tw": "Traditional Chinese (繁體中文)",
        "es": "Spanish (Español)",
        "kr": "Korean (한국어)",
        "vi": "Vietnamese (Tiếng Việt)",
        "pt-br": "Brazilian Portuguese (Português Brasileiro)",
        "fr": "Français (French)",
        "ru": "Русский (Russian)",
    }
    lang_text = language_map.get(language, "English")

    base_prompt = f"""
Analyze this GitHub repository {owner}/{repo} and create a wiki structure for it.

1. The complete file tree of the project:
<file_tree>
{file_tree}
</file_tree>

2. The README file of the project:
<readme>
{readme}
</readme>

I want to create a wiki for this repository. Determine the most logical structure for a wiki based on the repository's content.

IMPORTANT: The wiki content will be generated in {lang_text} language.

When designing the wiki structure, include pages that would benefit from visual diagrams, such as:
- Architecture overviews
- State machines
- Class hierarchies
"""
    if comprehensive:
        base_prompt += """
Create a structured wiki with the following main sections:
- Overview (general information about the project)
- System Architecture (how the system is designed)
- Core Features (key functionality)
- Data Management/Flow
- Frontend Components
- Backend Systems
- Model Integration
- Deployment/Infrastructure
- Extensibility and Customization

Return your analysis in the following XML format:

<wiki_structure>
  <title>[Overall title for the wiki]</title>
  <description>[Brief description of the repository]</description>
  <sections>
    <section id="section-1">
      <title>[Section title]</title>
      <pages>
        <page_ref>page-1</page_ref>
        <page_ref>page-2</page_ref>
      </pages>
      <subsections>
        <section_ref>section-2</section_ref>
      </subsections>
    </section>
  </sections>
  <pages>
    <page id="page-1">
      <title>[Page title]</title>
      <description>[Brief description of what this page will cover]</description>
      <importance>high|medium|low</importance>
      <relevant_files>
        <file_path>[Path to a relevant file]</file_path>
      </relevant_files>
      <related_pages>
        <related>page-2</related>
      </related_pages>
      <parent_section>section-1</parent_section>
    </page>
  </pages>
</wiki_structure>
"""
    else:
        base_prompt += """
Return your analysis in the following XML format:

<wiki_structure>
  <title>[Overall title for the wiki]</title>
  <description>[Brief description of the repository]</description>
  <pages>
    <page id="page-1">
      <title>[Page title]</title>
      <description>[Brief description of what this page will cover]</description>
      <importance>high|medium|low</importance>
      <relevant_files>
        <file_path>[Path to a relevant file]</file_path>
      </relevant_files>
      <related_pages>
        <related>page-2</related>
      </related_pages>
    </page>
  </pages>
</wiki_structure>
"""
    return base_prompt.strip()


def build_page_content_prompt(
    page_title: str,
    file_paths: list[str],
    language: str = "en",
    context: str = ""
) -> str:
    language_map = {
        "en": "English",
        "ja": "Japanese (日本語)",
        "zh": "Mandarin Chinese (中文)",
        "zh-tw": "Traditional Chinese (繁體中文)",
        "es": "Spanish (Español)",
        "kr": "Korean (한국어)",
        "vi": "Vietnamese (Tiếng Việt)",
        "pt-br": "Brazilian Portuguese (Português Brasileiro)",
        "fr": "Français (French)",
        "ru": "Русский (Russian)",
    }
    lang_text = language_map.get(language, "English")
 
    file_links = "\n".join(f"- [{path}](REPO_URL/{path})" for path in file_paths)
 
    return f"""
You are an expert technical writer and software architect.
Your task is to generate a comprehensive and accurate technical wiki page in Markdown format about a specific feature, system, or module within a given software project.
 
You will be given:
1. The "[WIKI_PAGE_TOPIC]" for the page you need to create.
2. A list of "[RELEVANT_SOURCE_FILES]" from the project that you MUST use as the sole basis for the content. You have access to the full content of these files. You MUST use AT LEAST 5 relevant source files for comprehensive coverage - if fewer are provided, search for additional related files in the codebase.
3. Additional retrieved "[RAG_CONTEXT]" that supplements the source files with relevant project knowledge.
 
CRITICAL STARTING INSTRUCTION:
The very first thing on the page MUST be a <details> block listing ALL the [RELEVANT_SOURCE_FILES] you used to generate the content. There MUST be AT LEAST 5 source files listed - if fewer were provided, you MUST find additional related files to include.
Format it exactly like this:
<details>
<summary>Relevant source files</summary>
 
The following files were used as context for generating this wiki page:
 
{file_links}
<!-- Add additional relevant files if fewer than 5 were provided -->
</details>
 
<details>
<summary>Retrieved additional context</summary>
 
{context}
</details>
 
Immediately after the <details> block, the main title of the page should be a H1 Markdown heading: # {page_title}.
 
Based ONLY on the content of the [RELEVANT_SOURCE_FILES] and [RAG_CONTEXT]:
 
1.  Introduction: Start with a concise introduction (1-2 paragraphs) explaining the purpose, scope, and high-level overview of "{page_title}" within the context of the overall project. If relevant, and if information is available in the provided files, link to other potential wiki pages using the format [Link Text](#page-anchor-or-id).
 
2.  Detailed Sections: Break down "{page_title}" into logical sections using H2 (`##`) and H3 (`###`) Markdown headings. For each section:
    *   Explain the architecture, components, data flow, or logic relevant to the section's focus, as evidenced in the source files.
    *   Identify key functions, classes, data structures, API endpoints, or configuration elements pertinent to that section.
 
3.  Mermaid Diagrams:
    *   EXTENSIVELY use Mermaid diagrams (e.g., flowchart TD, sequenceDiagram, classDiagram, erDiagram, `graph TD`) to visually represent architectures, flows, relationships, and schemas found in the source files.
    *   Ensure diagrams are accurate and directly derived from information in the [RELEVANT_SOURCE_FILES] and [RAG_CONTEXT].
    *   Provide a brief explanation before or after each diagram to give context.
    *   CRITICAL: All diagrams MUST follow strict vertical orientation:
       - Use "graph TD" (top-down) directive for flow diagrams
       - NEVER use "graph LR" (left-right)
       - Maximum node width should be 3-4 words
       - For sequence diagrams:
         - Start with "sequenceDiagram" directive on its own line
         - Define ALL participants at the beginning
         - Use descriptive but concise participant names
         - Use the correct arrow types:
           - ->> for request/asynchronous messages
           - -->> for response messages
           - -x for failed messages
         - Include activation boxes using +/- notation
         - Add notes for clarification using "Note over" or "Note right of"
 
4.  Tables:
    *   Use Markdown tables to summarize information such as:
        *   Key features or components and their descriptions.
        *   API endpoint parameters, types, and descriptions.
        *   Configuration options, their types, and default values.
        *   Data model fields, types, constraints, and descriptions.
 
5.  Code Snippets (ENTIRELY OPTIONAL):
    *   Include short, relevant code snippets (e.g., Python, Java, JavaScript, SQL, JSON, YAML) directly from the [RELEVANT_SOURCE_FILES] to illustrate key implementation details, data structures, or configurations.
    *   Ensure snippets are well-formatted within Markdown code blocks with appropriate language identifiers.
 
6.  Source Citations (EXTREMELY IMPORTANT):
    *   For EVERY piece of significant information, explanation, diagram, table entry, or code snippet, you MUST cite the specific source file(s) and relevant line numbers from which the information was derived.
    *   Place citations at the end of the paragraph, under the diagram/table, or after the code snippet.
    *   Use the exact format: Sources: [filename.ext:start_line-end_line]() for a range, or Sources: [filename.ext:line_number]() for a single line. Multiple files can be cited: Sources: [file1.ext:1-10](), [file2.ext:5](), [dir/file3.ext]() (if the whole file is relevant and line numbers are not applicable or too broad).
    *   IMPORTANT: You MUST cite AT LEAST 5 different source files throughout the wiki page to ensure comprehensive coverage.
 
7.  Technical Accuracy: All information must be derived SOLELY from the [RELEVANT_SOURCE_FILES] and [RAG_CONTEXT]. Do not infer, invent, or use external knowledge about similar systems or common practices unless it's directly supported by the provided code. If information is not present in the provided files, do not include it or explicitly state its absence if crucial to the topic.
 
8.  Clarity and Conciseness: Use clear, professional, and concise technical language suitable for other developers working on or learning about the project. Avoid unnecessary jargon, but use correct technical terms where appropriate.
 
9.  Conclusion/Summary: End with a brief summary paragraph if appropriate for "{page_title}", reiterating the key aspects covered and their significance within the project.
 
IMPORTANT: Generate the content in {lang_text} language.
 
Remember:
- Ground every claim in the provided source files and retrieved context.
- Prioritize accuracy and direct representation of the code's functionality and structure.
- Structure the document logically for easy understanding by other developers.
""".strip()