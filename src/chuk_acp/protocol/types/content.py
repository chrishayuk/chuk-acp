"""ACP content types - reuses MCP content types where possible."""

from typing import Optional, List, Literal, Union
from ..acp_pydantic_base import AcpPydanticBase, PYDANTIC_AVAILABLE

if PYDANTIC_AVAILABLE:
    from ..acp_pydantic_base import ConfigDict


class Annotations(AcpPydanticBase):
    """Optional metadata for content blocks."""

    audience: Optional[List[Literal["user", "assistant"]]] = None
    """Target audience for this content."""

    priority: Optional[float] = None
    """Priority level (0.0 to 1.0)."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class TextContent(AcpPydanticBase):
    """Plain text content block. All agents MUST support this."""

    type: Literal["text"] = "text"
    text: str
    annotations: Optional[Annotations] = None

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class ImageContent(AcpPydanticBase):
    """Image content block (base64-encoded). Requires 'image' prompt capability."""

    type: Literal["image"] = "image"
    data: str
    """Base64-encoded image data."""

    mimeType: str
    """MIME type (e.g., 'image/png', 'image/jpeg')."""

    uri: Optional[str] = None
    """Optional URI reference."""

    annotations: Optional[Annotations] = None

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class AudioContent(AcpPydanticBase):
    """Audio content block (base64-encoded). Requires 'audio' prompt capability."""

    type: Literal["audio"] = "audio"
    data: str
    """Base64-encoded audio data."""

    mimeType: str
    """MIME type (e.g., 'audio/wav', 'audio/mp3')."""

    annotations: Optional[Annotations] = None

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class TextResourceContents(AcpPydanticBase):
    """Text resource contents."""

    uri: str
    text: str
    mimeType: Optional[str] = None

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class BlobResourceContents(AcpPydanticBase):
    """Binary resource contents (base64-encoded)."""

    uri: str
    data: str
    """Base64-encoded binary data."""

    mimeType: Optional[str] = None

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class EmbeddedResource(AcpPydanticBase):
    """Embedded resource content block. Requires 'embeddedContext' prompt capability."""

    type: Literal["resource"] = "resource"
    resource: Union[TextResourceContents, BlobResourceContents]
    annotations: Optional[Annotations] = None

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class ResourceLink(AcpPydanticBase):
    """Resource link content block - references to resources agents can access."""

    type: Literal["resource_link"] = "resource_link"
    uri: str
    name: str
    mimeType: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    size: Optional[int] = None
    annotations: Optional[Annotations] = None

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


# Union type for any content block
Content = Union[
    TextContent,
    ImageContent,
    AudioContent,
    EmbeddedResource,
    ResourceLink,
]
