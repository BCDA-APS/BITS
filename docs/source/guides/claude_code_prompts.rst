.. _claude_code_prompts:

Claude Code Prompts for BITS Development
=========================================

This guide documents the specific prompts and best practices used with Claude Code for generating BITS tutorial content and development assistance.

Overview
--------

The BITS tutorial package (PR #159) was developed with AI assistance using Claude Code. This documentation provides transparency into the AI-assisted development process and helps others achieve similar results.

**Key Benefits of AI-Assisted Documentation:**
- Consistent structure and style across multiple guides
- Comprehensive coverage of complex topics
- Rapid prototyping and iteration
- Pattern recognition across similar frameworks

Documentation Generation Prompts
---------------------------------

**Primary Tutorial Generation Prompt:**

.. code-block:: text

    Create a comprehensive BITS tutorial that takes users from IOC exploration 
    to production deployment. The tutorial should be:
    
    1. **Progressive**: Each step builds on the previous
    2. **Practical**: All examples should work with containerized IOCs
    3. **Production-Ready**: Results in deployable instrument packages
    4. **Accessible**: Use ADSimDetector instead of hardware-specific examples
    
    Structure:
    - 00_introduction.md: Overview and learning objectives
    - 01_ioc_exploration.md: Device discovery and categorization
    - 02_bits_starter_setup.md: Using BITS-Starter template
    - 03_device_configuration.md: Mapping IOCs to Bluesky devices
    - 04_plan_development.md: Scientific measurement procedures
    - 05_ipython_execution.md: Interactive operation mastery
    
    Requirements:
    - Include validation scripts for each step
    - Provide troubleshooting sections
    - Use realistic but accessible examples
    - Follow BITS conventions and patterns

**Area Detector Documentation Prompt:**

.. code-block:: text

    Create comprehensive area detector documentation for BITS that:
    
    1. Uses ADSimDetector as primary example (accessible to all users)
    2. Includes notes about substituting actual detectors for production
    3. Covers apstools factory patterns and version compatibility
    4. Provides working examples that run in containers
    5. Includes troubleshooting and best practices
    
    Structure should include:
    - Quick start with 3-step setup
    - apstools factory usage
    - Version compatibility patterns
    - Common detector configurations
    - Integration with scan plans
    - Troubleshooting guide

**Code Example Generation Prompt:**

.. code-block:: text

    Generate Python code examples for BITS that:
    
    1. Follow BITS conventions (logging, import patterns, device creation)
    2. Use apstools when appropriate (don't reinvent existing functionality)
    3. Include proper error handling and validation
    4. Are immediately testable with simulation devices
    5. Include docstrings and comments explaining BITS-specific patterns
    
    For each example, provide:
    - Imports organized by BITS conventions
    - Class/function definition with BITS patterns
    - Configuration YAML snippet
    - Usage example with validation

Code Generation Best Practices
-------------------------------

**Effective Prompting Strategies:**

1. **Specify Framework Context:**
   
   .. code-block:: text
   
       "Create a BITS device using apstools patterns..."
       "Generate a Bluesky scan plan that follows BITS conventions..."

2. **Include Accessibility Requirements:**
   
   .. code-block:: text
   
       "Use SimDetector so examples work in any environment..."
       "Provide container-compatible IOC examples..."

3. **Request Validation:**
   
   .. code-block:: text
   
       "Include test cases that verify the implementation..."
       "Add validation steps to ensure proper setup..."

4. **Specify Output Format:**
   
   .. code-block:: text
   
       "Format as reStructuredText with code blocks..."
       "Include both Python code and YAML configuration..."

**Context-Aware Development:**

.. code-block:: text

    When working on BITS instruments, analyze the existing codebase patterns:
    
    1. Check how other devices are implemented in src/apsbits/demo_instrument/
    2. Follow the import patterns used in existing code
    3. Use the same logging conventions (logger.info(__file__))
    4. Match the directory structure and naming conventions
    5. Integrate with existing configuration patterns in iconfig.yml

Advanced Prompting Techniques
------------------------------

**Multi-Step Development Process:**

.. code-block:: text

    Phase 1: "Analyze the existing BITS framework structure and identify 
    patterns for device creation, plan development, and configuration management."
    
    Phase 2: "Based on the analysis, create a tutorial structure that guides 
    users through realistic instrument development scenarios."
    
    Phase 3: "Generate specific code examples for each tutorial section, 
    ensuring all examples use accessible simulation devices."
    
    Phase 4: "Create validation scripts and troubleshooting guides for 
    each tutorial component."

**Framework Integration Prompts:**

.. code-block:: text

    Integrate with BITS ecosystem by:
    
    1. Using apstools devices when available (check apstools.devices module)
    2. Following Bluesky plan conventions for scan development
    3. Integrating with databroker for data management
    4. Using ophyd Device patterns for hardware abstraction
    5. Following APS-specific conventions from apstools.utils

**Quality Assurance Prompts:**

.. code-block:: text

    Ensure code quality by:
    
    1. Including comprehensive docstrings with parameter descriptions
    2. Adding type hints for function signatures
    3. Following PEP 8 style guidelines
    4. Including error handling for common failure modes
    5. Providing usage examples with expected outputs

Documentation Iteration Process
-------------------------------

**Iterative Refinement Approach:**

1. **Initial Generation:**
   
   .. code-block:: text
   
       Generate initial documentation structure covering the main topics
       with placeholder content and basic examples.

2. **Content Development:**
   
   .. code-block:: text
   
       Expand each section with detailed examples, following the established
       patterns from existing BITS documentation.

3. **Example Validation:**
   
   .. code-block:: text
   
       Verify all code examples work with simulation devices and follow
       BITS conventions. Test import statements and configuration patterns.

4. **Integration Review:**
   
   .. code-block:: text
   
       Ensure documentation integrates well with existing guides and 
       maintains consistent style and terminology.

Common Patterns for BITS Development
-------------------------------------

**Device Creation Pattern:**

.. code-block:: text

    Create BITS device following this pattern:
    
    1. Import appropriate base classes (apstools preferred)
    2. Define device class with proper Component usage
    3. Include __init__ with BITS logging convention
    4. Add device-specific configuration methods
    5. Provide YAML configuration example
    6. Include usage example with validation

**Plan Development Pattern:**

.. code-block:: text

    Create Bluesky plan following this pattern:
    
    1. Import bluesky.plan_stubs for building blocks
    2. Use yield from for plan composition
    3. Include proper metadata collection
    4. Add parameter validation and error handling
    5. Provide usage examples with different devices
    6. Include troubleshooting notes

**Configuration Pattern:**

.. code-block:: text

    Create BITS configuration following this pattern:
    
    1. Use devices.yml for device instantiation
    2. Follow BITS naming conventions
    3. Include proper labels for categorization
    4. Separate development vs production configurations
    5. Provide validation scripts for configuration

Validation and Testing
----------------------

**Prompt for Test Generation:**

.. code-block:: text

    Create comprehensive tests for BITS components:
    
    1. Unit tests for device functionality using simulation
    2. Integration tests for plan execution
    3. Configuration validation scripts
    4. End-to-end workflow tests
    5. Performance and error handling tests

**Documentation Validation:**

.. code-block:: text

    Validate documentation by:
    
    1. Testing all code examples with simulation devices
    2. Verifying import statements work correctly
    3. Checking configuration files are valid YAML
    4. Ensuring examples follow BITS conventions
    5. Confirming accessibility for all users

Best Practices Summary
----------------------

**Effective AI-Assisted BITS Development:**

1. **Context First**: Always provide framework context and existing patterns
2. **Accessibility**: Use simulation devices for universal compatibility
3. **Validation**: Include testing and validation at each step
4. **Integration**: Ensure compatibility with existing BITS ecosystem
5. **Documentation**: Maintain transparency about AI assistance

**Quality Gates:**

- All examples must work with containerized simulation devices
- Code must follow established BITS conventions
- Documentation must integrate with existing guide structure
- Examples must be immediately testable by users
- Troubleshooting guidance must be comprehensive

**Continuous Improvement:**

.. code-block:: text

    Regularly update prompts based on:
    
    1. User feedback and common issues
    2. Framework evolution and new features
    3. Best practices discovered through usage
    4. Integration challenges and solutions
    5. Community contributions and suggestions

This documentation provides a foundation for effective AI-assisted BITS development while maintaining code quality and framework consistency.