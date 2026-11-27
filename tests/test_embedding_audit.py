import struct
import zipfile

from gemma4_agent.data.audit import _inspect_embeddings


def test_embedding_audit_reads_npy_shape_without_numpy(tmp_path):
    directory = tmp_path / "embeddings"
    directory.mkdir()
    npy_header = b"{'descr': '<f4', 'fortran_order': False, 'shape': (256,), }"
    padded_length = ((10 + len(npy_header) + 1 + 15) // 16) * 16 - 10
    header = npy_header + b" " * (padded_length - len(npy_header) - 1) + b"\n"
    npy = b"\x93NUMPY" + b"\x01\x00" + struct.pack("<H", len(header)) + header
    with zipfile.ZipFile(directory / "sample.npz", "w") as archive:
        archive.writestr("symbol.npy", npy)
    result = _inspect_embeddings(directory)
    assert result["shape_counts"] == {"(256,)": 1}
    assert result["malformed_files"] == 0
