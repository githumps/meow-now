# Meow Now - Development Rules & Guidelines

Operational rules for AI assistants working on the Meow Now project, inspired by SuperClaude framework.

## Priority Levels

- 🔴 **CRITICAL**: Security, data safety, production breaks - NEVER violate
- 🟡 **IMPORTANT**: Quality, maintainability, professionalism - Follow unless exceptional circumstances
- 🟢 **RECOMMENDED**: Optimization, style, best practices - Preferred approach

---

## 🔴 CRITICAL RULES

### Security & Safety

1. **Never commit secrets** to git
   - SIP credentials must stay in `.env` or `config/asterisk/sip.conf` (gitignored)
   - API keys, passwords, tokens go in `.env` only
   - Verify files before committing: `git diff --staged`

2. **Never push destructive changes** without explicit user confirmation
   - No `git push --force` to main/master
   - No `git reset --hard` without warning
   - No deletion of production data

3. **Validate audio file paths** to prevent path traversal
   - All audio paths must be within `audio/` directory
   - Use `Path().resolve()` and check parent directory

4. **Production database safety**
   - Never drop tables or databases
   - Always backup before schema changes
   - Use transactions for multi-step operations

### Code Integrity

5. **Never break existing functionality**
   - Run tests before committing if they exist
   - Verify imports work: `python -c "import module"`
   - Check syntax: `python -m py_compile file.py`

6. **Docker builds must succeed**
   - Test `docker build .` before pushing Dockerfile changes
   - Verify all dependencies in requirements.txt exist
   - Check multi-stage builds compile

---

## 🟡 IMPORTANT RULES

### Development Workflow

7. **Task Management Pattern**
   ```
   Understand → Plan → TodoWrite (3+ tasks) → Execute → Track → Validate
   ```
   - Always use TodoWrite for multi-step tasks (3+ tasks)
   - Mark tasks `in_progress` before starting
   - Mark `completed` immediately after finishing
   - Update status in real-time, don't batch

8. **Parallel Operations**
   - Use parallel tool calls for independent operations
   - Example: Multiple `Read` calls in one message
   - Example: `git status` + `git diff` together
   - Chain sequential operations: `cmd1 && cmd2 && cmd3`

9. **Evidence-Based Development**
   - Read official documentation before suggesting libraries
   - Test commands before recommending them
   - Verify file paths exist before editing
   - Check API documentation for correct usage

10. **Git Commit Standards**
    - Write clear, descriptive commit messages
    - Use conventional commits format:
      ```
      feat: Add new feature
      fix: Fix bug
      docs: Update documentation
      refactor: Refactor code
      test: Add tests
      chore: Maintenance tasks
      ```
    - Include context in commit body
    - Reference GitHub issues when applicable

11. **Context Offloading**
    - Create GitHub issues for all major features/tasks
    - Document decisions in ARCHITECTURE.md or relevant docs
    - Keep implementation details in code comments
    - Use GITHUB_ISSUES.md for roadmap tracking

### Code Quality

12. **Asterisk Configuration**
    - Always validate dialplan syntax before deploying
    - Test SIP configuration changes in development first
    - Document NAT/firewall requirements
    - Keep examples in comments for reference

13. **Audio Processing**
    - Validate sample rates match telephony (8kHz)
    - Check file formats are compatible with Asterisk
    - Handle missing audio files gracefully
    - Log audio generation errors clearly

14. **Error Handling**
    - Catch and log exceptions properly
    - Provide user-friendly error messages
    - Include troubleshooting hints in logs
    - Never silent-fail critical operations

15. **Documentation**
    - Update README.md when adding features
    - Keep DEPLOYMENT.md current with changes
    - Add inline comments for complex logic
    - Document environment variables in .env.example

---

## 🟢 RECOMMENDED RULES

### Code Style

16. **Python Conventions**
    - Follow PEP 8 style guide
    - Use type hints for function parameters
    - Keep functions under 50 lines when possible
    - Use descriptive variable names

17. **Docker Best Practices**
    - Multi-stage builds for smaller images
    - Layer caching for faster builds
    - `.dockerignore` to exclude unnecessary files
    - Security scanning for production images

18. **Testing**
    - Write tests for new features when applicable
    - Test audio generation functions
    - Verify voice analysis algorithms
    - Mock external dependencies (Asterisk, Ollama)

19. **Performance**
    - Profile audio processing for bottlenecks
    - Cache generated meow samples when appropriate
    - Use async/await for I/O operations
    - Monitor memory usage during calls

### Project Organization

20. **File Structure**
    - Keep related code in services/ modules
    - Configuration in config/
    - Scripts in scripts/
    - Documentation in docs/
    - Tests in tests/

21. **Dependency Management**
    - Pin versions in requirements.txt
    - Document optional dependencies clearly
    - Keep Docker base image updated
    - Regular security updates

22. **Logging**
    - Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
    - Include timestamps and context
    - Separate application and Asterisk logs
    - Rotate logs to prevent disk fill

---

## Development Patterns

### Task Execution Pattern

```python
# 1. UNDERSTAND
- Read existing code
- Check documentation
- Understand requirements

# 2. PLAN
- Break down into steps
- Identify parallel operations
- Consider edge cases

# 3. TODO
- Use TodoWrite for 3+ tasks
- Create specific, actionable items
- Set realistic estimates

# 4. EXECUTE
- One task at a time
- Test as you go
- Update status real-time

# 5. TRACK
- Mark completed immediately
- Note blockers/issues
- Document decisions

# 6. VALIDATE
- Run tests
- Check integration
- Verify documentation updated
```

### Parallel Tool Call Pattern

```python
# GOOD - Parallel independent operations
<function_calls>
  <invoke name="Read"><parameter name="file_path">file1.py