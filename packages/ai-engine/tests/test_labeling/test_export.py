from pathlib import Path

from ai_engine.labeling.export import YOLOExporter
from ai_engine.labeling.pre_labeler import PseudoLabel


class TestYOLOExport:
    def test_write_label_file(self, al_config, tmp_path):
        exporter = YOLOExporter(al_config)
        labels = [
            PseudoLabel(0.5, 0.5, 0.3, 0.3, 0, "rust", 0.9, "mock"),
            PseudoLabel(0.2, 0.8, 0.1, 0.1, 1, "damage", 0.7, "mock"),
        ]
        out = str(tmp_path / "test.txt")
        exporter.write_label_file("img.jpg", labels, out)
        content = Path(out).read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 2
        assert lines[0].startswith("0 ")
        assert lines[1].startswith("1 ")

    def test_generate_data_yaml(self, al_config, tmp_path):
        exporter = YOLOExporter(al_config)
        yaml_path = exporter.generate_data_yaml(str(tmp_path))
        assert Path(yaml_path).exists()
        content = Path(yaml_path).read_text()
        assert "rust" in content
        assert "nc: 5" in content

    def test_split_train_val_ratio(self, al_config):
        exporter = YOLOExporter(al_config)
        paths = [f"img_{i}.jpg" for i in range(100)]
        train, val = exporter.split_train_val(paths, val_ratio=0.2)
        assert len(train) == 80
        assert len(val) == 20
        assert set(train) & set(val) == set()

    def test_export_statistics(self, al_config, sample_labels):
        exporter = YOLOExporter(al_config)
        stats = exporter.export_statistics(sample_labels)
        assert stats["total_images"] == 10
        assert stats["total_labels"] == 10
        assert stats["avg_labels_per_image"] == 1.0
        assert "rust" in stats["class_distribution"]

    def test_full_export_creates_structure(self, al_config, tmp_image_dir, tmp_output_dir):
        exporter = YOLOExporter(al_config)
        labels = {}
        img_dir = Path(tmp_image_dir)
        for img in sorted(img_dir.glob("*.jpg"))[:5]:
            labels[str(img)] = [
                PseudoLabel(0.5, 0.5, 0.3, 0.3, 0, "rust", 0.9, "mock"),
            ]
        yaml_path = exporter.export(labels, tmp_output_dir)
        out = Path(tmp_output_dir)
        assert (out / "images" / "train").is_dir()
        assert (out / "images" / "val").is_dir()
        assert (out / "labels" / "train").is_dir()
        assert (out / "labels" / "val").is_dir()
        assert Path(yaml_path).exists()
