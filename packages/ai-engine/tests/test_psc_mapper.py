from ai_engine.inference.psc_mapper import PSCCodeMapper, Severity


class TestPSCCodeMapper:
    def setup_method(self):
        self.mapper = PSCCodeMapper()

    def test_rust_mapping(self):
        result = self.mapper.map_defect("rust", 0.9)
        assert result.psc_code == "0615"
        assert result.severity == Severity.CRITICAL

    def test_damage_mapping(self):
        result = self.mapper.map_defect("damage", 0.7)
        assert result.psc_code == "0630"
        assert result.severity == Severity.HIGH

    def test_leak_mapping(self):
        result = self.mapper.map_defect("leak", 0.5)
        assert result.psc_code == "0950"
        assert result.severity == Severity.MEDIUM

    def test_missing_label_mapping(self):
        result = self.mapper.map_defect("missing_label", 0.3)
        assert result.psc_code == "1320"
        assert result.severity == Severity.LOW

    def test_cargo_lashing_mapping(self):
        result = self.mapper.map_defect("cargo_lashing", 0.85)
        assert result.psc_code == "0725"
        assert result.severity == Severity.CRITICAL

    def test_unknown_defect_type(self):
        result = self.mapper.map_defect("unknown_type", 0.5)
        assert result.psc_code == "9999"

    def test_severity_boundary_critical(self):
        result = self.mapper.map_defect("rust", 0.8)
        assert result.severity == Severity.CRITICAL

    def test_severity_boundary_high(self):
        result = self.mapper.map_defect("rust", 0.6)
        assert result.severity == Severity.HIGH

    def test_severity_boundary_medium(self):
        result = self.mapper.map_defect("rust", 0.4)
        assert result.severity == Severity.MEDIUM

    def test_severity_boundary_low(self):
        result = self.mapper.map_defect("rust", 0.39)
        assert result.severity == Severity.LOW

    def test_severity_just_below_critical(self):
        result = self.mapper.map_defect("rust", 0.79)
        assert result.severity == Severity.HIGH

    def test_severity_just_below_high(self):
        result = self.mapper.map_defect("rust", 0.59)
        assert result.severity == Severity.MEDIUM

    def test_get_all_mappings(self):
        mappings = PSCCodeMapper.get_all_mappings()
        assert len(mappings) == 5
        assert mappings["rust"] == "0615"
        assert mappings["cargo_lashing"] == "0725"

    def test_custom_thresholds(self):
        mapper = PSCCodeMapper(
            critical_threshold=0.9,
            high_threshold=0.7,
            medium_threshold=0.5,
        )
        result = mapper.map_defect("rust", 0.85)
        assert result.severity == Severity.HIGH
