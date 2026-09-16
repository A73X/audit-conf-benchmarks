# audit-conf-benchmarks

**audit-conf-benchmarks** is a command-line tool and framework designed to help audit system configurations against security benchmarks, such as CIS Benchmarks.

It allows you to **parse machine configuration extracts**, **compare them against a specified benchmark (PDF or XLSX)**, and output compliance results in XLSX format. The project is built with extensibility in mind—new parsers and converters can be easily added to support different input formats and extraction tools.

⚖️ **Legal Notice:** Per Center for Internet Security (CIS) terms, CIS Benchmarks in PDF format may have restrictions on commercial use. Review and comply with the applicable CIS license/terms before any commercial use.

⚠️ **Note:** As of now, the tool only works for **Microsoft Windows configuration extracts**. Support for other platforms is planned in future updates.

---

## ✨ Features

- Accepts **CIS Benchmark files** in **PDF** or **XLSX** format.  
- Converts CIS Benchmark PDFs into structured XLSX files.  
- Parses machine extracts produced by [`audit-conf-extracts`](https://github.com/MatthisClavijo/audit-conf-extracts) (and can be extended with new parsers).  
- Compares extracted values with the benchmark requirements.  
- Outputs results in XLSX format showing machine values and compliance status.  
- Designed to be a **framework** where you can add your own parsers and converters.  

---

## 🚀 Usage

### Command-line
After installation, use the CLI:

```bash
audit-conf-benchmarks --benchmark /path/to/CIS_Benchmark.pdf --workdir /path/to/extract_workdir
```

or with short options:

```bash
audit-conf-benchmarks -b benchmark.xlsx -w ./workdir
```

### Arguments
- `--benchmark, -b` → Path to the benchmark file (PDF or XLSX).  
- `--workdir, -w` → The directory containing extracted configuration files to audit.  
- `--use-defaults, -d` → Evaluate compliance using the benchmark's documented default value when a key is not found on the machine.  

### Example
```bash
audit-conf-benchmarks -b CIS_Microsoft_Windows_10_Enterprise_Benchmark_v3.0.0.pdf -w ./DESKTOP-QUO897J/
```

---

## 📂 Output

The tool generates an **XLSX report** that includes:

- Extracted values from the target system.  
- Relevant benchmark requirements.  
- Compliance status (compliant / non-compliant / check manually).  

---

## 🛠 Extensibility

audit-conf-benchmarks is built as a **framework**:  

- **Parsers** → Add support for new extract formats beyond `audit-conf-extracts`.  
- **Converters** → Integrate support for different types of benchmarks or file formats besides CIS PDF.  

Contributions are welcome!  

---

## 📦 Installation (Work in Progress)

Clone the repository and run locally:

```bash
git clone https://github.com/A73X/audit-conf-benchmarks.git
cd audit-conf-benchmarks
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

Make the CLI executable:

```bash
chmod +x audit-conf-benchmarks.py
```

---

## ⚠️ Disclaimer

This project is a **work in progress**. Results should always be validated before being used for compliance assessment.  
It is designed to help audit system configurations and is not failproof—and never will be!  

⚠️ **Platform limitation:** Currently, the tool only works with **Microsoft Windows configuration extracts**.

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. See the [LICENSE](LICENSE) file for details.
