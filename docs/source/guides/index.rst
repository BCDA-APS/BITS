.. _guides:

BITS Guides & How-Tos
=====================

Comprehensive guides for BITS (Bluesky Instrument Template Structure) development, from quick start to advanced deployment patterns.

Getting Started
---------------

Essential guides to get your first BITS instrument running quickly.

.. toctree::
   :maxdepth: 2

   Quick Start Guide <quick_start>
   Creating Your First Instrument <creating_instrument>
   Installing BITS <../install>

Core Development
----------------

Build robust instruments with devices, plans, and configurations.

.. toctree::
   :maxdepth: 2

   Creating and Managing Devices <creating_devices>
   Area Detector Configuration <area_detectors>
   Creating Scan Plans <creating_plans>
   Configuration Management <configuration_management>
   Instrument Configuration <setting_iconfig>
   Common Instrument Patterns <common_instruments>

Advanced Topics
---------------

Production deployment, data management, and advanced patterns.

.. toctree::
   :maxdepth: 2

   Queue Server Configuration <qserver>
   Data Management Integration <dm>
   Production Deployment <deployment_patterns>
   Multi-Beamline Architecture <multi_beamline>

Development & Operations
------------------------

Developer tools, testing, and maintenance guides.

.. toctree::
   :maxdepth: 2

   BITS Framework Development <developing_bits>
   Testing Strategies <testing>
   Troubleshooting Guide <troubleshooting>
   Performance Optimization <performance>

Legacy and Migration
-------------------

Working with existing systems and migration paths.

.. toctree::
   :maxdepth: 2

   Template Creation (Legacy) <template_creation>
   Session Management <sessions>
   Queue Server Service <qserver_service>
   Instrument Startup <startup>

AI Integration
--------------

bAIt (Bluesky AI Tools) integration for intelligent deployment analysis.

.. toctree::
   :maxdepth: 2

   AI-Assisted Development <bait_integration>
   Automated Analysis <automated_analysis>
   Deployment Validation <deployment_validation>

Quick Reference
---------------

**Most Common Tasks:**

1. **Install BITS**: :doc:`3 commands to get started <../install>`
2. **Create Instrument**: :doc:`Basic to multi-beamline setups <creating_instrument>`
3. **Add Devices**: :doc:`Using apstools and custom patterns <creating_devices>`
4. **Configure Management**: :doc:`Declarative configuration with Guarneri <configuration_management>`
5. **Create Plans**: :doc:`From simple scans to complex workflows <creating_plans>`
6. **Deploy Production**: :doc:`Queue server and data management <qserver>`

**Architecture Patterns:**

- **Single Instrument**: Basic beamline setup
- **Multi-Endstation**: :doc:`Shared components pattern <common_instruments>`
- **Multi-Technique**: Complex beamline with many experimental methods
- **Production Deployment**: :doc:`Full data management integration <dm>`

**Development Workflow:**

1. :doc:`Create instrument structure <creating_instrument>`
2. :doc:`Configure devices and hardware <creating_devices>`
3. :doc:`Develop scan plans and procedures <creating_plans>`
4. :doc:`Set up data management <dm>`
5. :doc:`Deploy with queue server <qserver>`
6. :doc:`Monitor and maintain <troubleshooting>`

**Best Practices:**

- Use apstools devices when available (50+ pre-built classes)
- Follow BITS directory structure conventions
- Test with simulated devices before production
- Implement proper error handling and safety checks
- Include comprehensive metadata for data management

**AI-Powered Development:**

BITS integrates with bAIt (Bluesky AI Tools) for intelligent development assistance:

- Automated deployment analysis and validation
- Pattern recognition for common issues
- Optimization recommendations
- Documentation generation

See :doc:`bAIt Integration Guide <bait_integration>` for details.
