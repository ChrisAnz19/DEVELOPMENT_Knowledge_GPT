# Implementation Plan

- [x] 1. Upgrade model and enhance prompt engineering
  - Update the model parameter from GPT-3.5-Turbo to GPT-4-Turbo
  - Create a more detailed system prompt with clear instructions and examples
  - Add examples of good and bad behavioral reasons
  - Include specific guidance on avoiding unrealistic scenarios
  - Extract prompt building into a separate function
  - _Requirements: 1.1, 1.4, 3.1, 3.2, 4.1, 4.2, 4.3_

- [x] 2. Implement industry-specific and time-series behavior patterns
  - Create a function to determine candidate industry from title and company
  - Develop industry-specific behavioral templates with realistic scenarios
  - Implement templates for time-series behavioral patterns
  - Ensure patterns show progression or intent over time
  - _Requirements: 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 4.2, 4.4_

- [x] 3. Enhance fallback mechanism and response validation
  - Update the fallback logic to use industry-specific patterns
  - Incorporate time-series data in fallback assessments
  - Add validation for API responses against expected format
  - Implement detection of generic or unrealistic reasons
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 3.4_

- [x] 4. Optimize performance and implement testing
  - Review and optimize candidate data simplification for token efficiency
  - Implement efficient prompt construction
  - Write unit tests for the new functionality
  - Test the entire assessment pipeline with mock data
  - Compare results between GPT-3.5 and GPT-4-Turbo
  - _Requirements: 3.2, 3.3, 3.4_

- [x] 5. Final integration and documentation
  - Integrate all components into the main assess_and_return.py file
  - Update function signatures and docstrings
  - Add inline comments explaining the enhanced functionality
  - Create example usage documentation
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4_