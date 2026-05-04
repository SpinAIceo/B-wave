from pathlib import Path

import pytest

from ai_engine.labeling.pipeline import AdvancedALPipeline, PipelineStatus
from ai_engine.labeling.pre_labeler import PseudoLabel

requires_sam = pytest.mark.skip(reason="requires groundingdino and segment_anything")


class TestPipelineInit:
    def test_initialize_finds_images(self, al_config, tmp_image_dir):
        pipeline = AdvancedALPipeline(al_config)
        pipeline.initialize()
        assert len(pipeline._image_paths) == 20

    def test_embeddings_computed(self, al_config, tmp_image_dir):
        pipeline = AdvancedALPipeline(al_config)
        pipeline.initialize()
        assert pipeline._embeddings is not None
        assert pipeline._embeddings.shape[0] == 20


class TestPipelinePreLabeling:
    @requires_sam
    def test_pre_labeling_produces_labels(self, al_config, tmp_image_dir):
        pipeline = AdvancedALPipeline(al_config)
        pipeline.initialize()
        pipeline.run_pre_labeling()
        assert len(pipeline._labels) > 0


class TestPipelineBatchSelection:
    def test_initial_batch(self, al_config, tmp_image_dir):
        pipeline = AdvancedALPipeline(al_config)
        pipeline.initialize()
        batch = pipeline.select_initial_batch()
        assert len(batch) == al_config.initial_batch_size

    @requires_sam
    def test_subsequent_batch(self, al_config, tmp_image_dir):
        pipeline = AdvancedALPipeline(al_config)
        pipeline.initialize()
        pipeline.run_pre_labeling()
        pipeline.train_al_model()
        batch = pipeline.select_batch()
        assert len(batch) <= al_config.batch_size


class TestPipelineRound:
    @requires_sam
    def test_full_round(self, al_config, tmp_image_dir):
        pipeline = AdvancedALPipeline(al_config)
        pipeline.initialize()
        pipeline.run_pre_labeling()

        batch = pipeline.select_initial_batch()
        human_labels = {
            p: [
                PseudoLabel(0.5, 0.5, 0.3, 0.3, 0, "rust", 0.95, "human"),
            ]
            for p in batch
        }
        pipeline.submit_human_labels(batch, human_labels)
        acc = pipeline.train_al_model()
        assert 0 <= acc <= 1

    @requires_sam
    def test_should_stop_after_max_rounds(self, al_config, tmp_image_dir):
        al_config.max_rounds = 1
        pipeline = AdvancedALPipeline(al_config)
        pipeline.initialize()
        pipeline.run_pre_labeling()
        pipeline.train_al_model()
        assert pipeline.should_stop()


class TestPipelineStatus:
    def test_status_structure(self, al_config, tmp_image_dir):
        pipeline = AdvancedALPipeline(al_config)
        pipeline.initialize()
        status = pipeline.get_status()
        assert isinstance(status, PipelineStatus)
        assert status.total_images == 20
        assert status.current_round == 0


class TestPipelinePersistence:
    @requires_sam
    def test_save_and_load(self, al_config, tmp_image_dir, tmp_path):
        pipeline = AdvancedALPipeline(al_config)
        pipeline.initialize()
        pipeline.run_pre_labeling()

        state_path = str(tmp_path / "state.json")
        pipeline.save_state(state_path)
        assert Path(state_path).exists()

        pipeline2 = AdvancedALPipeline(al_config)
        pipeline2.initialize()
        pipeline2.load_state(state_path)
        assert pipeline2._round == pipeline._round
        assert len(pipeline2._labels) == len(pipeline._labels)


class TestPipelineExport:
    @requires_sam
    def test_export_produces_yaml(self, al_config, tmp_image_dir, tmp_output_dir):
        pipeline = AdvancedALPipeline(al_config)
        pipeline.initialize()
        pipeline.run_pre_labeling()
        yaml_path = pipeline.export_dataset()
        assert Path(yaml_path).exists()
