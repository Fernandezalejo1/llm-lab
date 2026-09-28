#!/usr/bin/env python3
"""sitecustomize del lab: se auto-importa en todo script Python que corra desde
este directorio. Parchea bugs del build de torch ROCm de AMD para Windows
(torch._C._distributed_c10d ausente).

El build oficial de torch 2.11+rocm7.13 para Windows NO trae el C-ext
torch._C._distributed_c10d, y torch.distributed es un stub casi vacio
(sin Store/Backend/Work). Cualquier import real de la pila distributed
(accelerate -> torchao -> funcol -> distributed_c10d, trl GRPO -> FSDP,
trl vllm_client -> distributed_c10d) revienta. En single-GPU el lab NUNCA
usa distributed: todos los shims son inertes a nivel de import.

ORDEN CRITICO: los shims se registran en sys.modules ANTES de importar
accelerate (que ya arrastra torchao en su import de utils/ao.py).
"""

import sys
import types as _types


# ============ SHIMS (se registran antes de cualquier import de accelerate) ===

# --- shim torch._C._distributed_c10d --------------------------------------
if "torch._C._distributed_c10d" not in sys.modules:
    _mod = _types.ModuleType("torch._C._distributed_c10d")
    _mod.__file__ = "<lab-shim>"

    class _FakeProcessGroup:
        @classmethod
        def _create_internal(cls, group_rank=0, group_size=1, backend_opts=None):
            return cls()

        def allreduce(self, *a, **k):
            raise NotImplementedError("FakeProcessGroup shim: no comunicacion real")

        def broadcast(self, *a, **k):
            raise NotImplementedError("FakeProcessGroup shim: no comunicacion real")

    class _Options:
        def __init__(self, *a, **k):
            pass

    class _Backend:
        Options = _Options
        FAKE = "fake"

        @classmethod
        def register_backend(cls, *a, **k):
            pass

    _mod.FakeProcessGroup = _FakeProcessGroup
    _mod.Backend = _Backend
    sys.modules["torch._C._distributed_c10d"] = _mod

# --- shim torch.distributed.fsdp ------------------------------------------
if "torch.distributed.fsdp" not in sys.modules:
    _fsdp = _types.ModuleType("torch.distributed.fsdp")
    _fsdp.__file__ = "<lab-shim>"

    class _FullyShardedDataParallel:
        @staticmethod
        def summon_full_params(*a, **k):
            raise NotImplementedError("FSDP shim: no hay sharding en el lab")

        @staticmethod
        def _get_fsdp_state(*a, **k):
            raise NotImplementedError("FSDP shim: no hay sharding en el lab")

    _fsdp.FullyShardedDataParallel = _FullyShardedDataParallel
    sys.modules["torch.distributed.fsdp"] = _fsdp

# --- shim torch.distributed._functional_collectives ------------------------
if "torch.distributed._functional_collectives" not in sys.modules:
    _funcol = _types.ModuleType("torch.distributed._functional_collectives")
    _funcol.__file__ = "<lab-shim>"

    class _AsyncCollectiveTensor:
        def __init__(self, *a, **k):
            raise NotImplementedError(
                "AsyncCollectiveTensor shim: no hay colectivas async en el lab"
            )

    _funcol.AsyncCollectiveTensor = _AsyncCollectiveTensor
    sys.modules["torch.distributed._functional_collectives"] = _funcol

# --- shim torch.distributed.distributed_c10d -------------------------------
if "torch.distributed.distributed_c10d" not in sys.modules:
    _c10d = _types.ModuleType("torch.distributed.distributed_c10d")
    _c10d.__file__ = "<lab-shim>"

    class _Options:
        def __init__(self, *a, **k):
            pass

    class _ProcessGroup:
        def __init__(self, *a, **k):
            pass

    class _Store:
        def __init__(self, *a, **k):
            pass

    _c10d.ProcessGroup = _ProcessGroup
    _c10d.Store = _Store
    _c10d.PrefixStore = _Store
    _c10d.FileStore = _Store
    _c10d.HashStore = _Store
    _c10d.TCPStore = _Store
    _c10d.ProcessGroupXCCL = _ProcessGroup
    _c10d.ProcessGroupNCCL = _ProcessGroup
    _c10d.ProcessGroupGloo = _ProcessGroup
    _c10d.ProcessGroupMPI = _ProcessGroup
    _c10d.ProcessGroupUCC = _ProcessGroup
    _c10d.GroupName = str
    _c10d.ReduceOp = type("ReduceOp", (), {})
    _c10d.Work = type("Work", (), {})
    _c10d.DebugLevel = type("DebugLevel", (), {})
    _c10d._DistributedBackendOptions = _Options
    _c10d.AllgatherOptions = _Options
    _c10d.AllreduceOptions = _Options
    _c10d.AllreduceCoalescedOptions = _Options
    _c10d.AllToAllOptions = _Options
    _c10d.BarrierOptions = _Options
    _c10d.BroadcastOptions = _Options
    _c10d.GatherOptions = _Options
    _c10d.ReduceOptions = _Options
    _c10d.ReduceScatterOptions = _Options
    _c10d.ScatterOptions = _Options

    def _noop(*a, **k):
        return None

    _c10d.get_debug_level = _noop
    _c10d.set_debug_level = _noop
    _c10d.set_debug_level_from_env = _noop
    _c10d.init_process_group = _noop
    _c10d.is_initialized = lambda *a, **k: False
    _c10d.get_rank = lambda *a, **k: 0
    _c10d.get_world_size = lambda *a, **k: 1
    _c10d.new_group = _noop
    _c10d.split_group = _noop
    _c10d.get_backend = _noop
    _c10d._get_default_group = _noop
    _c10d._resolve_process_group = _noop
    _c10d.get_process_group_ranks = lambda *a, **k: []
    _c10d._register_process_group = _noop
    _c10d._unregister_process_group = _noop
    _c10d._unregister_all_process_groups = _noop
    _c10d._register_handler = _noop
    sys.modules["torch.distributed.distributed_c10d"] = _c10d

# --- shim torch.distributed._tensor (torchao.float8 - DTensor) -------------
if "torch.distributed._tensor" not in sys.modules:
    _dt = _types.ModuleType("torch.distributed._tensor")
    _dt.__file__ = "<lab-shim>"

    class _DTensor:
        """Inerte: accelerate hace isinstance() checks; con un stub jamas
        matchea, exactamente lo que quiere el lab (nada de distribuido)."""

        def __init__(self, *a, **k):
            raise NotImplementedError("DTensor shim: el lab no usa DTensor")

    _dt.DTensor = _DTensor
    sys.modules["torch.distributed._tensor"] = _dt

# --- cortar torchao en transformers (quantizers/auto.py) --------------------
if "transformers.quantizers.quantizer_torchao" not in sys.modules:
    _qt = _types.ModuleType("transformers.quantizers.quantizer_torchao")
    _qt.__file__ = "<lab-shim>"

    class _TorchAoHfQuantizer:
        def __init__(self, *a, **k):
            raise NotImplementedError(
                "TorchAoHfQuantizer shim: el lab no cuantiza con torchao"
            )

    _qt.TorchAoHfQuantizer = _TorchAoHfQuantizer
    sys.modules["transformers.quantizers.quantizer_torchao"] = _qt

# --- cortar torchao en accelerate (utils/ao.py importa torchao.float8) ------
if "accelerate.utils.ao" not in sys.modules:
    _ao = _types.ModuleType("accelerate.utils.ao")
    _ao.__file__ = "<lab-shim>"

    def _no_ao_layers(*a, **k):
        return False

    def _pass(*a, **k):
        return None

    _ao.has_ao_layers = _no_ao_layers
    _ao.filter_first_and_last_linear_layers = _pass
    _ao.convert_model_to_fp8_ao = _pass
    _ao.find_first_last_linear_layers = _pass
    _ao.filter_linear_layers = _pass
    sys.modules["accelerate.utils.ao"] = _ao

# --- cortar trl.mergekit_utils (mergekit revienta con pydantic 2.13) --------
# trl 0.24 importa mergekit en MODULE-LEVEL (trl/trainer/callbacks.py:40:
# `from ..mergekit_utils import MergeConfig, merge_models, upload_model_to_hf`).
# mergekit/merge_methods/easy_define.py hace pydantic.create_model(Task[Tensor])
# y pydantic 2.13 no genera schema para torch.Tensor -> el import de trl muere.
# El lab (single-GPU GRPO) NO usa merge: stub inerte como los demás shims.
if "trl.mergekit_utils" not in sys.modules:
    _mk = _types.ModuleType("trl.mergekit_utils")
    _mk.__file__ = "<lab-shim>"

    class _MergeConfig:
        def __init__(self, *a, **k):
            raise NotImplementedError("mergekit shim: el lab no mergea con mergekit")

    def _merge_models(*a, **k):
        raise NotImplementedError("mergekit shim: el lab no mergea con mergekit")

    def _upload_model_to_hf(*a, **k):
        raise NotImplementedError("mergekit shim: el lab no sube modelos")

    _mk.MergeConfig = _MergeConfig
    _mk.merge_models = _merge_models
    _mk.upload_model_to_hf = _upload_model_to_hf
    sys.modules["trl.mergekit_utils"] = _mk


# ============ PATCHES sobre paquetes ya presentes ==========================

# --- accelerate DTensor -----------------------------------------------------
import accelerate.utils.other as _acc_other
import accelerate.accelerator as _acc_acc

if not hasattr(_acc_other, "_lab_dtensor_patched"):
    _acc_other.model_has_dtensor = lambda _model: False
    _acc_acc.model_has_dtensor = _acc_other.model_has_dtensor
    _acc_other._lab_dtensor_patched = True

# --- transformers 5.5: _is_package_available devuelve tupla siempre ---------
# transformers 5.5 cambió el contrato: con return_version=False devuelve
# (bool, None) en vez de bool pelado. Eso rompe dos frentes:
#  - trl la llama esperando bool -> (False, None) es TRUTHY -> cree que todos
#    los paquetes opcionales están instalados (llm_blender, etc.).
#  - transformers interno (is_peft_available) espera la tupla -> hace [0].
# Solución: envolver el resultado en un objeto que es falsy/truthy correcto
# (contracto viejo), indexable [0]/[1] e iterable (contracto nuevo 5.5).
import transformers.utils.import_utils as _ihf_iu

if not hasattr(_ihf_iu, "_lab_ipa_patched"):
    _ihf_iu_orig = _ihf_iu._is_package_available

    class _LabPkgBool:
        __slots__ = ("ok", "version")

        def __init__(self, ok, version=None):
            self.ok = bool(ok)
            self.version = version

        def __bool__(self):
            return self.ok

        def __getitem__(self, idx):
            if idx == 0:
                return self.ok
            if idx == 1:
                return self.version
            raise IndexError(f"index {idx} out of range para _LabPkgBool")

        def __iter__(self):
            yield self.ok
            yield self.version

        def __repr__(self):
            return f"_LabPkgBool({self.ok!r}, {self.version!r})"

    def _lab_ipa(pkg_name: str, return_version: bool = False):
        res = _ihf_iu_orig(pkg_name, return_version)
        if return_version:
            return res  # tupla real, contrato 5.5 para quien la pide
        if isinstance(res, tuple):
            return _LabPkgBool(res[0], res[1])
        return _LabPkgBool(res)

    _ihf_iu._is_package_available = _lab_ipa
    _ihf_iu._lab_ipa_patched = True