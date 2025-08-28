
import re
import tempfile
import subprocess
import os

def convert_with_soffice(
    file_bytes: bytes,
    origin_ext: str,
    dest_ext: str,
    timeout: int = 120
) -> bytes:

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, f"input{origin_ext}")
        output_path = os.path.join(tmpdir, f"input{dest_ext}")

        # Save input file
        with open(input_path, "wb") as f:
            f.write(file_bytes)

        # r"C:\Program Files\LibreOffice\program\soffice.exe", 
        # r"soffice", 
        # Run LibreOffice headless to convert
        cmd = [
            r"soffice",  # adjust path if on Linux → "soffice"
            "--headless",
            "--convert-to", dest_ext.lstrip("."),  # e.g., "docx", "pdf"
            "--outdir", tmpdir,
            input_path
        ]

        try:
            completed = subprocess.run(
                cmd, check=True, capture_output=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            raise TimeoutError(
                f"LibreOffice conversion timed out after {timeout} seconds."
            )
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.decode(errors="ignore")
            raise RuntimeError(f"LibreOffice conversion failed: {err_msg}")

        # Verify output exists
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Conversion failed: output {dest_ext} file not found")

        with open(output_path, "rb") as f:
            return f.read()
