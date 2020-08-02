import argparse
import concurrent.futures
import multiprocessing
import os
import pathlib as pth
import subprocess
import logging


# logger = logging.getLogger(__name__)

# # c_handler = logging.FileHandler('file.log')
# c_handler = logging.StreamHandler()
# c_handler.setLevel(logging.INFO)
# c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# c_handler.setFormatter(c_format)
# logger.addHandler(c_handler)
import sys


class Convert(object):
    def __init__(self, path_to_heic_f_dir: str, result_path: str):
        self.heic_files_dir = self.check_path(path_to_heic_f_dir)
        self.result_path = self.create_res_path(result_path)

    def check_path(self, income_path: str) -> pth:
        income_p = pth.Path(income_path)
        if not os.path.exists(income_p):
            raise OSError(f'Path incorrect or not exist!: {income_path}')
        return income_p

    def create_res_path(self, res_path: str):
        try:
            self.check_path(res_path)
        except OSError as os_err:
            print(f'Result path not exist! {res_path} err {os_err}')
            os.makedirs(res_path)
            print(f'Result path created! {res_path}')
        finally:
            return pth.Path(res_path)

    def list_of_files(self) -> list:
        data_files_list = [
            str(self.heic_files_dir/item) for item in os.listdir(
                self.heic_files_dir) if item.endswith('.heic') or item.endswith('.HEIC')
        ]
        return data_files_list

    def jpd_file_from_data_file(self, data_file: pth):
        print(f'REss PAth: {self.result_path}')
        print(f'datafile {data_file}')
        return str(self.result_path / f'{str(data_file).split("/")[-1].split(".")[0]}.jpg')

    def transform(self, data_file_path: pth):
        res_path = self.jpd_file_from_data_file(str(data_file_path))
        print(f'Transform path: {res_path}')
        p = subprocess.run(
            ['heif-convert', f'{data_file_path}', f'{res_path}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )
        if p.stderr:
            raise FileExistsError(f'Error {p.stderr}')
        # print(f'Result {p.stdout}')

    def processors_count(self) -> int:
        cpu = multiprocessing.cpu_count()
        available_cpu = cpu-2
        if available_cpu <= 0:
            return 1
        else:
            return available_cpu

    def multiprocess_heic_to_jpg(self):
        list_of_f = self.list_of_files()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.processors_count()) as executor:
            future_to_args = {executor.submit(self.transform, image_arg): image_arg for image_arg in
                              list_of_f}

            for future in concurrent.futures.as_completed(future_to_args):
                image_arg = future_to_args[future]
                try:
                    future.result()
                except Exception as exc:
                    print(f'Saving image '
                          f'{image_arg} generated an '
                          f'exception: {exc}')
                else:
                    print(f'Image '
                          f'{self.jpd_file_from_data_file(image_arg)} '
                          f'saved successfully.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Heic to jpg')

    parser.add_argument('-i', '--input', action="store", dest="input", required=True)
    parser.add_argument('-o', '--output', action="store", dest="output", required=True)
    arguments = parser.parse_args()
    Convert(arguments.input, arguments.output).multiprocess_heic_to_jpg()

