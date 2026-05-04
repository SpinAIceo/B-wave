from ai_engine.labeling.config import ALConfig, default_class_prompts


class TestALConfig:
    def test_default_classes(self):
        cfg = ALConfig(image_dir=".", output_dir=".")
        assert len(cfg.class_names) == 5
        assert "rust" in cfg.class_names
        assert "cargo_lashing" in cfg.class_names

    def test_default_thresholds(self):
        cfg = ALConfig(image_dir=".", output_dir=".")
        assert cfg.confidence_threshold_auto == 0.7
        assert cfg.confidence_threshold_discard == 0.3
        assert cfg.target_accuracy == 0.90

    def test_custom_values(self):
        cfg = ALConfig(
            image_dir="/data",
            output_dir="/out",
            num_clusters=10,
            batch_size=50,
        )
        assert cfg.num_clusters == 10
        assert cfg.batch_size == 50


class TestDefaultPrompts:
    def test_has_all_classes(self):
        prompts = default_class_prompts()
        for cls in ["rust", "damage", "leak", "missing_label", "cargo_lashing"]:
            assert cls in prompts
            assert len(prompts[cls]) >= 2

    def test_prompts_are_strings(self):
        prompts = default_class_prompts()
        for cls, texts in prompts.items():
            for t in texts:
                assert isinstance(t, str)
                assert len(t) > 3
