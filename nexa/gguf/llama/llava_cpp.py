from __future__ import annotations

import ctypes
import functools
from ctypes import _Pointer  # type: ignore
from ctypes import (
    POINTER,
    Structure,
    c_bool,
    c_char_p,
    c_float,
    c_int,
    c_uint8,
    c_void_p,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    List,
    NewType,
    Optional,
    TypeVar,
    Union,
)

from typing_extensions import TypeAlias

import nexa.gguf.llama.llama_cpp as llama_cpp
from nexa.gguf.lib_utils import load_library

# Specify the base name of the shared library to load
_libllava_base_name = "llava"

# Load the library
_libllava = load_library(_libllava_base_name)

# ctypes helper

if TYPE_CHECKING:
    CtypesCData = TypeVar("CtypesCData", bound=ctypes._CData)  # type: ignore

    CtypesArray: TypeAlias = ctypes.Array[CtypesCData]  # type: ignore

    CtypesPointer: TypeAlias = ctypes._Pointer[CtypesCData]  # type: ignore

    CtypesVoidPointer: TypeAlias = ctypes.c_void_p

    class CtypesRef(Generic[CtypesCData]):
        pass

    CtypesPointerOrRef: TypeAlias = Union[
        CtypesPointer[CtypesCData], CtypesRef[CtypesCData]
    ]

    CtypesFuncPointer: TypeAlias = ctypes._FuncPointer  # type: ignore

F = TypeVar("F", bound=Callable[..., Any])


def ctypes_function_for_shared_library(lib: ctypes.CDLL):
    def ctypes_function(
        name: str, argtypes: List[Any], restype: Any, enabled: bool = True
    ):
        def decorator(f: F) -> F:
            if enabled:
                func = getattr(lib, name)
                func.argtypes = argtypes
                func.restype = restype
                functools.wraps(f)(func)
                return func
            else:
                return f

        return decorator

    return ctypes_function


ctypes_function = ctypes_function_for_shared_library(_libllava)


################################################
# llava.h
################################################

# struct clip_ctx;
clip_ctx_p = NewType("clip_ctx_p", int)
clip_ctx_p_ctypes = c_void_p


# struct llava_image_embed {
#     float * embed;
#     int n_image_pos;
# };
class llava_image_embed(Structure):
    _fields_ = [
        ("embed", POINTER(c_float)),
        ("n_image_pos", c_int),
    ]


# /** sanity check for clip <-> llava embed size match */
# LLAVA_API bool llava_validate_embed_size(const llama_context * ctx_llama, const clip_ctx * ctx_clip);
@ctypes_function(
    "llava_validate_embed_size",
    [llama_cpp.llama_context_p_ctypes, clip_ctx_p_ctypes],
    c_bool,
)
def llava_validate_embed_size(
    ctx_llama: llama_cpp.llama_context_p, ctx_clip: clip_ctx_p, /
) -> bool: ...


# /** build an image embed from image file bytes */
# LLAVA_API struct llava_image_embed * llava_image_embed_make_with_bytes(struct clip_ctx * ctx_clip, int n_threads, const unsigned char * image_bytes, int image_bytes_length);
@ctypes_function(
    "llava_image_embed_make_with_bytes",
    [clip_ctx_p_ctypes, c_int, POINTER(c_uint8), c_int],
    POINTER(llava_image_embed),
)
def llava_image_embed_make_with_bytes(
    ctx_clip: clip_ctx_p,
    n_threads: Union[c_int, int],
    image_bytes: CtypesArray[c_uint8],
    image_bytes_length: Union[c_int, int],
    /,
) -> "_Pointer[llava_image_embed]": ...


# /** build an image embed from a path to an image filename */
# LLAVA_API struct llava_image_embed * llava_image_embed_make_with_filename(struct clip_ctx * ctx_clip, int n_threads, const char * image_path);
@ctypes_function(
    "llava_image_embed_make_with_filename",
    [clip_ctx_p_ctypes, c_int, c_char_p],
    POINTER(llava_image_embed),
)
def llava_image_embed_make_with_filename(
    ctx_clip: clip_ctx_p, n_threads: Union[c_int, int], image_path: bytes, /
) -> "_Pointer[llava_image_embed]": ...


# LLAVA_API void llava_image_embed_free(struct llava_image_embed * embed);
# /** free an embedding made with llava_image_embed_make_* */
@ctypes_function("llava_image_embed_free", [POINTER(llava_image_embed)], None)
def llava_image_embed_free(embed: "_Pointer[llava_image_embed]", /): ...


# /** write the image represented by embed into the llama context with batch size n_batch, starting at context pos n_past. on completion, n_past points to the next position in the context after the image embed. */
# LLAVA_API bool llava_eval_image_embed(struct llama_context * ctx_llama, const struct llava_image_embed * embed, int n_batch, int * n_past);
@ctypes_function(
    "llava_eval_image_embed",
    [
        llama_cpp.llama_context_p_ctypes,
        POINTER(llava_image_embed),
        c_int,
        POINTER(c_int),
    ],
    c_bool,
)
def llava_eval_image_embed(
    ctx_llama: llama_cpp.llama_context_p,
    embed: "_Pointer[llava_image_embed]",
    n_batch: Union[c_int, int],
    n_past: "_Pointer[c_int]",
    /,
) -> bool: ...


################################################
# clip.h
################################################


# /** load mmproj model */
# CLIP_API struct clip_ctx * clip_model_load    (const char * fname, int verbosity);
@ctypes_function("clip_model_load", [c_char_p, c_int], clip_ctx_p_ctypes)
def clip_model_load(
    fname: bytes, verbosity: Union[c_int, int], /
) -> Optional[clip_ctx_p]: ...


# /** free mmproj model */
# CLIP_API void clip_free(struct clip_ctx * ctx);
@ctypes_function("clip_free", [clip_ctx_p_ctypes], None)
def clip_free(ctx: clip_ctx_p, /): ...