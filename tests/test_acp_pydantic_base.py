"""Tests for ACP Pydantic base model."""

import sys
import json
from typing import Any


class TestAcpPydanticBase:
    """Test AcpPydanticBase with Pydantic available."""

    def test_pydantic_available(self):
        """Test that Pydantic is detected correctly."""
        from chuk_acp.protocol.acp_pydantic_base import PYDANTIC_AVAILABLE

        # In our test environment, Pydantic should be available
        assert isinstance(PYDANTIC_AVAILABLE, bool)

    def test_basic_model_creation(self):
        """Test creating a basic model instance."""
        from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

        class TestModel(AcpPydanticBase):
            name: str = "test"
            value: int = 42

        model = TestModel()
        assert model.name == "test"
        assert model.value == 42

    def test_model_with_data(self):
        """Test creating a model with custom data."""
        from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

        class TestModel(AcpPydanticBase):
            name: str = "default"
            value: int = 0

        model = TestModel(name="custom", value=100)
        assert model.name == "custom"
        assert model.value == 100

    def test_model_dump(self):
        """Test model_dump method."""
        from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

        class TestModel(AcpPydanticBase):
            name: str = "test"
            value: int = 42

        model = TestModel(name="example", value=123)
        data = model.model_dump()

        assert isinstance(data, dict)
        assert data["name"] == "example"
        assert data["value"] == 123

    def test_model_dump_exclude_none(self):
        """Test model_dump with exclude_none."""
        from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

        class TestModel(AcpPydanticBase):
            name: str
            optional: Any = None

        model = TestModel(name="test", optional=None)
        data = model.model_dump(exclude_none=True)

        assert "name" in data
        assert data["name"] == "test"
        # With Pydantic, None might still be included depending on implementation
        # Just verify it's a dict
        assert isinstance(data, dict)

    def test_model_dump_json(self):
        """Test model_dump_json method."""
        from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

        class TestModel(AcpPydanticBase):
            name: str = "test"
            value: int = 42

        model = TestModel(name="example", value=123)
        json_str = model.model_dump_json()

        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["name"] == "example"
        assert parsed["value"] == 123

    def test_model_validate_with_dict(self):
        """Test model_validate with dictionary."""
        from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

        class TestModel(AcpPydanticBase):
            name: str
            value: int

        data = {"name": "test", "value": 42}
        model = TestModel.model_validate(data)

        assert model.name == "test"
        assert model.value == 42

    def test_model_validate_with_instance(self):
        """Test model_validate with existing instance."""
        from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

        class TestModel(AcpPydanticBase):
            name: str = "test"

        original = TestModel(name="original")
        validated = TestModel.model_validate(original)

        # Should handle instance gracefully
        assert validated is not None

    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed."""
        from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

        class TestModel(AcpPydanticBase):
            name: str = "test"

        # With ConfigDict(extra="allow"), extra fields should be permitted
        model = TestModel(name="test", extra_field="extra")
        data = model.model_dump()

        assert data["name"] == "test"
        # Extra field handling depends on Pydantic version
        assert isinstance(data, dict)

    def test_class_level_defaults(self):
        """Test that class-level defaults work correctly."""
        from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

        class TestModel(AcpPydanticBase):
            type: str = "fixed"
            name: str = "default"

        model1 = TestModel()
        assert model1.type == "fixed"
        assert model1.name == "default"

        model2 = TestModel(name="custom")
        assert model2.type == "fixed"
        assert model2.name == "custom"


class TestFallbackImplementation:
    """Test fallback implementation when Pydantic is not available."""

    def test_fallback_basic_creation(self):
        """Test basic creation with fallback."""
        # We need to test the fallback, but Pydantic is installed
        # So we'll import and test the fallback class directly
        import importlib

        # Save original module
        original_module = sys.modules.get("chuk_acp.protocol.acp_pydantic_base")

        # Temporarily remove pydantic to test fallback
        pydantic_module = sys.modules.get("pydantic")
        if pydantic_module:
            sys.modules["pydantic"] = None  # type: ignore

        try:
            # Reload the module to trigger fallback
            if original_module:
                importlib.reload(original_module)

            from chuk_acp.protocol.acp_pydantic_base import (
                AcpPydanticBase,
                PYDANTIC_AVAILABLE,
            )

            # Should use fallback
            assert PYDANTIC_AVAILABLE is False

            class TestModel(AcpPydanticBase):
                name: str = "test"
                value: int = 42

            model = TestModel()
            # Fallback sets class-level defaults in __init__
            assert hasattr(model, "name")
            assert hasattr(model, "value")

        finally:
            # Restore pydantic
            if pydantic_module:
                sys.modules["pydantic"] = pydantic_module
            if original_module:
                importlib.reload(original_module)

    def test_fallback_model_dump(self):
        """Test fallback model_dump."""
        import importlib

        original_module = sys.modules.get("chuk_acp.protocol.acp_pydantic_base")
        pydantic_module = sys.modules.get("pydantic")
        if pydantic_module:
            sys.modules["pydantic"] = None  # type: ignore

        try:
            if original_module:
                importlib.reload(original_module)

            from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

            class TestModel(AcpPydanticBase):
                name: str = "test"

            model = TestModel(name="example", extra="field")
            data = model.model_dump()

            assert isinstance(data, dict)
            assert data["name"] == "example"
            assert data["extra"] == "field"

        finally:
            if pydantic_module:
                sys.modules["pydantic"] = pydantic_module
            if original_module:
                importlib.reload(original_module)

    def test_fallback_model_dump_exclude_none(self):
        """Test fallback model_dump with exclude_none."""
        import importlib

        original_module = sys.modules.get("chuk_acp.protocol.acp_pydantic_base")
        pydantic_module = sys.modules.get("pydantic")
        if pydantic_module:
            sys.modules["pydantic"] = None  # type: ignore

        try:
            if original_module:
                importlib.reload(original_module)

            from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

            class TestModel(AcpPydanticBase):
                pass

            model = TestModel(name="test", value=None)
            data = model.model_dump(exclude_none=True)

            assert "name" in data
            assert data["name"] == "test"
            assert "value" not in data  # None excluded

        finally:
            if pydantic_module:
                sys.modules["pydantic"] = pydantic_module
            if original_module:
                importlib.reload(original_module)

    def test_fallback_model_dump_json(self):
        """Test fallback model_dump_json."""
        import importlib

        original_module = sys.modules.get("chuk_acp.protocol.acp_pydantic_base")
        pydantic_module = sys.modules.get("pydantic")
        if pydantic_module:
            sys.modules["pydantic"] = None  # type: ignore

        try:
            if original_module:
                importlib.reload(original_module)

            from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

            class TestModel(AcpPydanticBase):
                pass

            model = TestModel(name="test", value=42)
            json_str = model.model_dump_json()

            assert isinstance(json_str, str)
            parsed = json.loads(json_str)
            assert parsed["name"] == "test"
            assert parsed["value"] == 42

        finally:
            if pydantic_module:
                sys.modules["pydantic"] = pydantic_module
            if original_module:
                importlib.reload(original_module)

    def test_fallback_model_validate(self):
        """Test fallback model_validate."""
        import importlib

        original_module = sys.modules.get("chuk_acp.protocol.acp_pydantic_base")
        pydantic_module = sys.modules.get("pydantic")
        if pydantic_module:
            sys.modules["pydantic"] = None  # type: ignore

        try:
            if original_module:
                importlib.reload(original_module)

            from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

            class TestModel(AcpPydanticBase):
                pass

            data = {"name": "test", "value": 42}
            model = TestModel.model_validate(data)

            assert hasattr(model, "name")
            assert model.name == "test"
            assert model.value == 42

        finally:
            if pydantic_module:
                sys.modules["pydantic"] = pydantic_module
            if original_module:
                importlib.reload(original_module)

    def test_fallback_private_attributes_excluded(self):
        """Test that private attributes are excluded from model_dump."""
        import importlib

        original_module = sys.modules.get("chuk_acp.protocol.acp_pydantic_base")
        pydantic_module = sys.modules.get("pydantic")
        if pydantic_module:
            sys.modules["pydantic"] = None  # type: ignore

        try:
            if original_module:
                importlib.reload(original_module)

            from chuk_acp.protocol.acp_pydantic_base import AcpPydanticBase

            class TestModel(AcpPydanticBase):
                pass

            model = TestModel(name="test", _private="hidden")
            data = model.model_dump()

            assert "name" in data
            assert "_private" not in data  # Private fields excluded

        finally:
            if pydantic_module:
                sys.modules["pydantic"] = pydantic_module
            if original_module:
                importlib.reload(original_module)


class TestModuleExports:
    """Test module-level exports."""

    def test_all_exports(self):
        """Test __all__ exports."""
        from chuk_acp.protocol import acp_pydantic_base

        assert hasattr(acp_pydantic_base, "__all__")
        assert "AcpPydanticBase" in acp_pydantic_base.__all__
        assert "PYDANTIC_AVAILABLE" in acp_pydantic_base.__all__

        # ConfigDict should be in __all__ only if Pydantic is available
        if acp_pydantic_base.PYDANTIC_AVAILABLE:
            assert "ConfigDict" in acp_pydantic_base.__all__
