import numpy as np

from ai_engine.labeling.simclr_init import SimCLRInitializer


class TestClustering:
    def test_cluster_count(self, al_config, random_embeddings):
        init = SimCLRInitializer(al_config)
        labels = init.cluster_images(random_embeddings)
        assert len(labels) == len(random_embeddings)
        assert len(set(labels)) <= al_config.num_clusters

    def test_cluster_distribution(self, al_config, random_embeddings):
        init = SimCLRInitializer(al_config)
        init.cluster_images(random_embeddings)
        dist = init.get_cluster_distribution()
        assert sum(dist.values()) == len(random_embeddings)


class TestBatchSelection:
    def test_batch_size(self, al_config, random_embeddings):
        init = SimCLRInitializer(al_config)
        labels = init.cluster_images(random_embeddings)
        paths = [f"img_{i}.jpg" for i in range(len(random_embeddings))]
        batch = init.select_initial_batch(
            paths, random_embeddings, labels, al_config.initial_batch_size
        )
        assert len(batch) == al_config.initial_batch_size

    def test_batch_items_are_paths(self, al_config, random_embeddings):
        init = SimCLRInitializer(al_config)
        labels = init.cluster_images(random_embeddings)
        paths = [f"img_{i}.jpg" for i in range(len(random_embeddings))]
        batch = init.select_initial_batch(paths, random_embeddings, labels, 5)
        for item in batch:
            assert item in paths

    def test_batch_unique(self, al_config, random_embeddings):
        init = SimCLRInitializer(al_config)
        labels = init.cluster_images(random_embeddings)
        paths = [f"img_{i}.jpg" for i in range(len(random_embeddings))]
        batch = init.select_initial_batch(paths, random_embeddings, labels, 5)
        assert len(batch) == len(set(batch))


class TestEmbeddings:
    def test_fallback_shape(self, al_config):
        init = SimCLRInitializer(al_config)
        paths = [f"img_{i}.jpg" for i in range(10)]
        emb = init._compute_embeddings_fallback(paths)
        assert emb.shape == (10, al_config.simclr_embedding_dim)

    def test_fallback_normalized(self, al_config):
        init = SimCLRInitializer(al_config)
        paths = [f"img_{i}.jpg" for i in range(10)]
        emb = init._compute_embeddings_fallback(paths)
        norms = np.linalg.norm(emb, axis=1)
        np.testing.assert_allclose(norms, 1.0, atol=1e-5)
