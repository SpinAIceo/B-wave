"""Download additional datasets from Roboflow for B-Wave training."""

from roboflow import Roboflow

API_KEY = "l3BkaB8yLTbIk8eYYroI"

DATASETS = [
    # Leak reinforcement
    {
        "workspace": "daisycat1008-outlook-com",
        "project": "oil-spill-detection-q6qid",
        "version": 1,
        "output": "data/raw/roboflow-oil-spill",
        "desc": "Oil Spill Detection (daisycat1008)",
    },
    {
        "workspace": "chris-mxxpq",
        "project": "detect-oil-spill",
        "version": 1,
        "output": "data/raw/roboflow-oil-spill2",
        "desc": "Detect Oil Spill (chris)",
    },
    {
        "workspace": "gas-leak",
        "project": "pipeline-leak-prediction",
        "version": 1,
        "output": "data/raw/roboflow-pipe-leak",
        "desc": "Pipeline Leak Prediction",
    },
    # Cargo lashing
    {
        "workspace": "wirerope-qfgck",
        "project": "wire-rope-defect-f4qyg",
        "version": 1,
        "output": "data/raw/roboflow-wire-rope",
        "desc": "Wire Rope Defect",
    },
    {
        "workspace": "learning-dvrz6",
        "project": "fastener-defect-detection",
        "version": 1,
        "output": "data/raw/roboflow-fastener",
        "desc": "Fastener Defect Detection",
    },
    # Missing label
    {
        "workspace": "fire-extinguisher",
        "project": "fireextinguisher-z5atr",
        "version": 1,
        "output": "data/raw/roboflow-fire-safety",
        "desc": "Fire Safety Equipment",
    },
]


def main():
    rf = Roboflow(api_key=API_KEY)

    for ds in DATASETS:
        print(f"\n{'='*60}")
        print(f"Downloading: {ds['desc']}")
        print(f"  {ds['workspace']}/{ds['project']} v{ds['version']}")
        print(f"  -> {ds['output']}")
        try:
            project = rf.workspace(ds["workspace"]).project(ds["project"])
            version = project.version(ds["version"])
            version.download("yolov11", location=ds["output"])
            print(f"  OK")
        except Exception as e:
            print(f"  FAILED: {e}")
            print(f"  Trying other versions...")
            try:
                project = rf.workspace(ds["workspace"]).project(ds["project"])
                versions = project.versions()
                if versions:
                    latest = versions[0]
                    print(f"  Trying version {latest.version}...")
                    latest.download("yolov11", location=ds["output"])
                    print(f"  OK (v{latest.version})")
                else:
                    print(f"  No versions available")
            except Exception as e2:
                print(f"  FAILED completely: {e2}")

    print(f"\n{'='*60}")
    print("All downloads complete.")


if __name__ == "__main__":
    main()
