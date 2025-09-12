from CONVERTERS.cis_benchmark_converter import CisBenchmarkConverter
from check_extractor import CheckExtractor
from parser_manager import ParserManager
from searcher import Searcher
from comparator import Comparator
from xlsx_writer import XlsxWriter
from helper import Helper
import os

class Orchestrator:
    def __init__(self, benchmark_path, workdir):
        self.helper = Helper()
        self.__regkeys_per_file_d = {}
        self.__values_d = {}
        self.__proofs_d = {}
        self.benchmark_path = benchmark_path
        self.workdir = workdir
        self.checkExtractor = CheckExtractor()
        self.searcher = Searcher(self.workdir)
        self.parserManager = ParserManager()
        self.comparator = Comparator()
        self.xlsxWriter = XlsxWriter()
        
    def __check_benchmark(self, benchmark_path):
        try:
            benchmark_extension = os.path.splitext(benchmark_path)[1].lower()

            if benchmark_extension == ".pdf":
                converter = CisBenchmarkConverter()
                benchmark_xlsx = converter.convert(benchmark_path, "xlsx")
                return benchmark_xlsx
            elif benchmark_extension == ".xlsx":
                return benchmark_path
            else:
                raise ValueError("Unsupported benchmark file type : " + benchmark_extension)
        except FileNotFoundError:
            print(f"Error: The file '{benchmark_path}' cannot be found.")
            return None

    def __update_regkeys_per_file_dict(self, found_files_l, regkey):
        for file in found_files_l:
            if file in self.__regkeys_per_file_d:
                self.__regkeys_per_file_d[file].append(regkey)
            else:
                self.__regkeys_per_file_d[file] = [regkey]

    def __update_values(self, found_values_d):
        for regkey in found_values_d:
            if regkey in self.__values_d:
                self.__values_d[regkey].append(found_values_d[regkey])
            else:
                self.__values_d[regkey] = [found_values_d[regkey]]

    def __update_proofs(self, found_proofs_d):
        for regkey in found_proofs_d:
            if regkey in self.__proofs_d:
                self.__proofs_d[regkey].append(found_proofs_d[regkey])
            else:
                self.__proofs_d[regkey] = [found_proofs_d[regkey]]

    def audit(self):
        self.benchmark_path = self.__check_benchmark(self.benchmark_path)
        self.checkExtractor.extract_checks_from_xlsx(self.benchmark_path)
        self.searcher.set_not_unique_key_l(self.checkExtractor.not_unique_key_l)
        self.searcher.list_all_files(self.workdir)

        self.helper.log_info("Starting search phase for parsable files")
        log_counter = 1
        log_max = len([reg for check in self.checkExtractor.checks_l for reg in check])
        log_files_count = len(self.searcher.workdir_files_l)
        for check in self.checkExtractor.checks_l:
            for regkey in check:
                self.helper.log_info(f"Searching for parsable files. Searched {log_counter}/{log_max} times through {log_files_count} files", end="\r", flush=True)
                log_counter += 1
                try:
                    keyword = self.searcher.regkey_to_keyword(regkey)
                    found_files_l = self.searcher.search_keyword_insensitive(keyword)
                    # Update dict in orchestrator
                    self.__update_regkeys_per_file_dict(found_files_l, regkey)
                except Exception as e:
                    print(f"Keyword error : {keyword} Exception: {e}")
        print()
        self.helper.log_info("End of search phase for parsable files")

        self.helper.log_info("Starting parse phase")
        for file, regkeys_l in self.__regkeys_per_file_d.items():
            found_values_d, found_proofs_d = self.parserManager.parse(file, regkeys_l)
            self.__update_values(found_values_d)
            self.__update_proofs(found_proofs_d)
        self.helper.log_info("End of parse phase")

        self.comparator.set_checks_l(self.checkExtractor.checks_l)
        self.comparator.set_checks_values_d(self.checkExtractor.checks_values_d)
        self.comparator.set_values_d(self.__values_d)
        compliance_l, reason_l = self.comparator.eval_compliance()

        self.xlsxWriter.set_benchmark_xlsx_path(self.benchmark_path)
        self.xlsxWriter.write(self.checkExtractor.checks_l, self.__values_d, self.__proofs_d, compliance_l, reason_l)