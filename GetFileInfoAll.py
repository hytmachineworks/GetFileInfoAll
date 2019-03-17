# coding = utf-8
"""
create on : 2019/03/02
project name : GetFileInfoAll
file name : GetFileInfoAll

"""
from datetime import datetime as dt
from pathlib import Path
import time

from tqdm import tqdm
from tinydb import TinyDB

TIME_FORMAT = "%Y/%m/%d %H:%M:%S"


def start_db(table_name):
    """ start up tinyDB

    :param table_name: database table name string
    :return: database dict
    """

    # start db
    db = TinyDB("DirFileInfo.json")

    table_name_normalize = table_name.replace("/", "\\")

    # select table
    db_table = db.table(table_name_normalize)

    result_dict = {"db": db_table, "table_name": table_name_normalize}

    return result_dict


def search_dir_files(db_table, this_floor_path_list, level):
    """ search files in directory

    :param db_table: database table class
    :param this_floor_path_list: target directory windows path object
    :param level: dir level int
    :return: next level file and dir list
    """

    def search_subdir(target_path, dir_list):
        """ search sub-directory items

        :param target_path: check item path windows path object
        :param dir_list: next search dir list
        :return: next dir list, item info dict
        """

        target_path_str = str(target_path)

        error_str = ""

        try:
            if target_path.is_symlink():
                # ignore symbolic link
                pass

            if target_path.is_dir():
                # when dir
                target_path_type = "dir"

                target_path_stat = target_path.stat()
                last_access = dt.fromtimestamp(target_path_stat.st_atime)
                file_create = dt.fromtimestamp(target_path_stat.st_ctime)
                last_modify = dt.fromtimestamp(target_path_stat.st_mtime)

                file_size = 0

                dir_list.append(target_path)

            else:
                # when file
                target_path_type = "file"

                target_path_stat = target_path.stat()
                last_access = dt.fromtimestamp(target_path_stat.st_atime)
                file_create = dt.fromtimestamp(target_path_stat.st_ctime)
                last_modify = dt.fromtimestamp(target_path_stat.st_mtime)

                file_size = target_path_stat.st_size

        except Exception as error:
            replace_path_str = target_path_str.replace("\\", "\\\\")
            error_str = str(error).replace(replace_path_str, "Path strings")

            target_path_type = "error"

            last_access = dt.fromtimestamp(0.0)
            file_create = dt.fromtimestamp(0.0)
            last_modify = dt.fromtimestamp(0.0)

            file_size = 0

        target_path_dict = {"path": target_path_str,
                            "path_type": target_path_type,
                            "level": level,
                            "last_access": last_access.strftime(TIME_FORMAT),
                            "file_create": file_create.strftime(TIME_FORMAT),
                            "last_modify": last_modify.strftime(TIME_FORMAT),
                            "size": file_size}

        if error_str:
            target_path_dict["error_description"] = error_str

        # db_table.insert(target_path_dict)

        return dir_list, target_path_dict

    next_floor_dir_list = []
    target_path_dict_list = []

    for this_floor_path in tqdm(this_floor_path_list):

        # search all file and dirs
        path_list = list(this_floor_path.glob("*"))

        for path in path_list:
            # search file information
            path_info_tuple = search_subdir(path, next_floor_dir_list)

            next_floor_dir_list, target_dict = path_info_tuple

            target_path_dict_list.append(target_dict)

    db_table.insert_multiple(target_path_dict_list)

    return next_floor_dir_list


def search_dir_file_info(search_target):
    """ search every item on target directory

    :param search_target: search start directory string
    :return: message string
    """

    # initialize database
    db_dict = start_db(search_target)
    db_table = db_dict["db"]
    search_target_normalize = db_dict["table_name"]

    db_table.purge()

    # initialize search condition
    next_floor_dir_list = [Path(search_target_normalize).resolve()]

    total_count = target_count = level = 1

    output_str = "\nlevel no.{no} / count:{item} / total:{total}"

    while target_count > 0:

        time.sleep(1)

        print(output_str.format(no=str(level).zfill(2),
                                item=str(target_count),
                                total=str(total_count)))

        time.sleep(1)

        next_floor_dir_list = search_dir_files(db_table,
                                               next_floor_dir_list, level)

        target_count = len(next_floor_dir_list)

        total_count += target_count

        level += 1

    return "program finished"


def main():
    drive_str = "C:/"

    print(search_dir_file_info(drive_str))


if __name__ == "__main__":
    main()
