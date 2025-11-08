"""Base Pydantic model for ACP types with optional Pydantic support."""

from typing import Any

try:
    from pydantic import BaseModel, ConfigDict

    PYDANTIC_AVAILABLE = True

    class AcpPydanticBase(BaseModel):  # type: ignore[misc]
        """Base Pydantic model for ACP types."""

        model_config = ConfigDict(extra="allow")

except ImportError:
    PYDANTIC_AVAILABLE = False

    class AcpPydanticBase:  # type: ignore
        """Fallback base class when Pydantic is not available."""

        def __init__(self, **data: Any):
            # First, set class-level defaults (like type="text")
            for key in dir(self.__class__):
                if not key.startswith("_") and not callable(getattr(self.__class__, key)):
                    class_value = getattr(self.__class__, key)
                    # Only set if it's a simple type (not a class or method)
                    if isinstance(class_value, (str, int, float, bool, type(None))):
                        setattr(self, key, class_value)

            # Then, override with provided data
            for key, value in data.items():
                setattr(self, key, value)

        def model_dump(self, exclude_none: bool = False, **kwargs: Any) -> dict[str, Any]:
            """Convert model to dictionary."""
            result = {}
            for key, value in self.__dict__.items():
                if key.startswith("_"):
                    continue
                if exclude_none and value is None:
                    continue
                result[key] = value
            return result

        def model_dump_json(self, **kwargs: Any) -> str:
            """Convert model to JSON string."""
            import json

            return json.dumps(self.model_dump(**kwargs))

        @classmethod
        def model_validate(cls, data: Any) -> "AcpPydanticBase":
            """Create instance from dictionary."""
            if isinstance(data, dict):
                return cls(**data)
            return data  # type: ignore[no-any-return]


__all__ = ["AcpPydanticBase", "PYDANTIC_AVAILABLE"]

if PYDANTIC_AVAILABLE:
    __all__.append("ConfigDict")
