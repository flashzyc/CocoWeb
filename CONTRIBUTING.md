# Contributing to CocoWeb Open Source Community

Thank you for considering contributing to this repository.

This project is a **community-style repository** that includes:

- the core `CocoWeb` security lab
- member-contributed engineering projects
- course-driven and practice-driven experiments

Because of that, contributions may involve documentation, navigation, code cleanup, new projects, screenshots, or feature improvements.

## Ways to Contribute

You can help by:

- improving documentation and repository navigation
- fixing bugs in existing subprojects
- adding setup guides, screenshots, or demo notes
- improving tests, code quality, or project structure
- contributing new member projects
- refining project descriptions in `PROJECTS.md`

## Before You Start

Please keep these principles in mind:

- Respect the original structure of each subproject unless a change is clearly beneficial.
- Avoid breaking unrelated parts of the repository.
- Prefer small, reviewable pull requests.
- Document non-obvious setup steps and assumptions.
- If a project includes intentionally vulnerable code for teaching purposes, do not "silently secure" it without explaining the impact.

## Recommended Contribution Workflow

1. Fork the repository.
2. Create a new branch for your changes.
3. Make focused updates.
4. Update relevant documentation.
5. Open a Pull Request with a clear summary.

## Pull Request Checklist

Before opening a PR, please check:

- The change has a clear purpose.
- Related documentation has been updated if needed.
- File names and folder names remain understandable.
- New files are placed in the correct project directory.
- No secrets, credentials, or local config files are included.

## Adding a New Member Project

If you want to add a new member project, please:

1. Place it under `成员代码/`.
2. Use a folder name that clearly identifies the author and the project.
3. Include a `README.md` inside the project directory.
4. Document:
   - what the project does
   - the main stack
   - how to run it
   - current status or limitations
5. Add or update the entry in `PROJECTS.md`.

## Documentation Style

For top-level documentation:

- Prefer concise and readable GitHub-style Markdown.
- Bilingual content is welcome when it improves accessibility.
- Use headings and short sections instead of long unstructured text.

## Security and Safety

This repository contains a security playground intended for **authorized learning and local testing only**.

- Do not propose changes that encourage misuse.
- Do not upload real secrets or production credentials.
- Be explicit when a change affects the teaching purpose of a vulnerable example.

## License

By contributing to this repository, you agree that your contributions will be licensed under the terms of the [MIT License](./LICENSE).
