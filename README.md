#  Decision Space Explorer





[Streamlit App](awerqwer)



DecisionSupportLibrary/
│
├── streamlit_app.py
├── config.py
│
├── core/
│   ├── input_panel.py
│   ├── enrichment.py
│   ├── framing.py
│   ├── workspace_controls.py
│   ├── workspace.py
│   ├── workspace_summary.py
│   ├── workspace_maps.py
│   └── workspace_dataset.py
│
├── lenses/
│   ├── lenses.py              # UI común de selección de lens
│   ├── lens_engine.py         # aplica la lens activa
│   ├── lens_feedback.py       # pinta feedback de cada lens
│   ├── lens_registry.py       # registro central de lenses
│   ├── lens_preference.py
│   ├── lens_diversity.py
│   ├── lens_efficiency.py
│   └── lens_indicator.py      # antes lens_domain.py
│
├── plugins/
│   ├── __init__.py
│   ├── nrp_plugin.py
│   └── aerospace_plugin.py
│
├── soi/
│   └── soi_registry.py
│
└── ui/
    └── visualization.py


##  Overview

## 💻 Running Locally

To run this dashboard on your local machine:

1. Clone the repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
