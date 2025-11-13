
DEFAULT_DOF = "Roll"
DEFAULT_Y_METRIC = "amplitude"
PERIOD_WINDOW_DEFAULT = (3.0, 60.0)  # [s]

# Recognized names (case-insensitive) for the parameter study directory
PARAM_STUDY_DIR_HINTS = [
    "ParameterStudy", "Parameter Study", "Parameter_Study",
    "ParameterStudies", "ParamStudy", "Param_Study",
]

# Regex for run folder names (e.g., '0-20251111144055' or 'run-20251111...')
RUN_DIR_REGEX = r'^(?:0-|run-)?\d{8,}$'
