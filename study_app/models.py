from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

EntryKind = Literal["ax", "df", "rk", "th", "pb"]
SupplementKind = Literal["pf", "sl"]


class LoginRequest(BaseModel):
    password: str = Field(min_length=1, max_length=4096)


class FolderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=64)
    parent_id: str | None = None
    index: int | None = Field(default=None, ge=0, le=100_000)

    @field_validator("name")
    @classmethod
    def name_is_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("folder name cannot be blank")
        return value


class FolderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    slug: str | None = Field(default=None, min_length=1, max_length=64)
    parent_id: str | None = None
    review_enabled: bool | None = None

    @field_validator("name")
    @classmethod
    def name_is_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("folder name cannot be blank")
        return value

    @field_validator("slug")
    @classmethod
    def slug_is_not_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("folder slug cannot be null")
        return value


class EntryCreate(BaseModel):
    folder_id: str = Field(min_length=1, max_length=128)
    index: int | None = Field(default=None, ge=0, le=100_000)
    kind: EntryKind
    title: str = Field(min_length=1, max_length=240)
    tag: str = Field(min_length=1, max_length=80)
    header: str = Field(default="", max_length=4000)
    review_modes: list[str] | None = Field(default=None, max_length=12)
    content: str = Field(default="", max_length=8_000_000)

    @field_validator("title")
    @classmethod
    def title_is_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("entry title cannot be blank")
        return value


class EntryUpdate(BaseModel):
    folder_id: str | None = Field(default=None, min_length=1, max_length=128)
    kind: EntryKind | None = None
    title: str | None = Field(default=None, min_length=1, max_length=240)
    tag: str | None = Field(default=None, min_length=1, max_length=80)
    header: str | None = Field(default=None, max_length=4000)
    review_modes: list[str] | None = Field(default=None, max_length=12)
    problem_family: str | None = Field(default=None, max_length=120)
    confusable_with: list[str] | None = Field(default=None, max_length=100)

    @field_validator("title")
    @classmethod
    def title_is_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("entry title cannot be blank")
        return value


class VariantCreate(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    subtag: str | None = Field(default=None, max_length=80)
    content: str = Field(default="", max_length=8_000_000)
    main: bool = False

    @field_validator("label")
    @classmethod
    def label_is_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("variant label cannot be blank")
        return value


class VariantUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=120)
    subtag: str | None = Field(default=None, max_length=80)
    content: str | None = Field(default=None, max_length=8_000_000)
    main: bool | None = None

    @field_validator("label")
    @classmethod
    def label_is_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("variant label cannot be blank")
        return value


class SupplementCreate(BaseModel):
    kind: SupplementKind
    label: str = Field(min_length=1, max_length=120)
    subtag: str | None = Field(default=None, max_length=80)
    content: str = Field(default="", max_length=8_000_000)
    main: bool = False

    @field_validator("label")
    @classmethod
    def label_is_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("supplement label cannot be blank")
        return value


class ContentUpdate(BaseModel):
    content: str = Field(max_length=8_000_000)


class MarkdownRenderRequest(BaseModel):
    source: str = Field(max_length=8_000_000)
    folder_id: str | None = Field(default=None, max_length=128)


class MoveRequest(BaseModel):
    destination_folder_id: str | None
    index: int = Field(default=0, ge=0)


class ReorderRequest(BaseModel):
    entry_ids: list[str] = Field(max_length=100_000)


class MacrosUpdate(BaseModel):
    macros: dict[str, str | list[str | int]] = Field(max_length=1000)


class ReviewReveal(BaseModel):
    attempt: str = Field(default="", max_length=20000)
    confidence: int = Field(strict=True, ge=1, le=3)
    elapsed_ms: int = Field(default=0, ge=0, le=86_400_000)
    overt: bool = True
    hints_used: int = Field(default=0, ge=0, le=20)


class ReviewGrade(BaseModel):
    grade: int = Field(ge=0, le=3)
    attempt_id: str = Field(min_length=32, max_length=32, pattern=r"^[a-f0-9]{32}$")


class GitCommitRequest(BaseModel):
    message: str = Field(min_length=1, max_length=240)

    @field_validator("message")
    @classmethod
    def message_is_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("commit message cannot be blank")
        return value


class ExportRequest(BaseModel):
    folder_id: str | None = None
    recursive: bool = True
    kinds: list[EntryKind] = Field(
        default_factory=lambda: ["ax", "df", "rk", "th", "pb"], min_length=1
    )
    include_supplements: bool = True
    title: str | None = Field(default=None, max_length=240)


class DiagramNode(BaseModel):
    id: str = Field(min_length=1, max_length=32)
    label: str = Field(max_length=500)
    row: int = Field(ge=0, le=4)
    column: int = Field(ge=0, le=4)


class DiagramArrow(BaseModel):
    source: str = Field(min_length=1, max_length=32)
    target: str = Field(min_length=1, max_length=32)
    label: str = Field(default="", max_length=500)
    dashed: bool = False
    double: bool = False


class CommutativeDiagramCreate(BaseModel):
    name: str = Field(default="Commutative diagram", min_length=1, max_length=240)
    width: int = Field(default=76, ge=10, le=100)
    nodes: list[DiagramNode] = Field(min_length=1, max_length=25)
    arrows: list[DiagramArrow] = Field(default_factory=list, max_length=80)

    @field_validator("name")
    @classmethod
    def name_is_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("diagram name cannot be blank")
        return value
