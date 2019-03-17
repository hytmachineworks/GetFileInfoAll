# coding = utf-8
"""
create on : 2019/03/09
project name : GetFileInfoAll
file name : QueryFileInfo 

"""
from pprint import pprint
from pathlib import Path

from tqdm import tqdm

from tinydb import Query

from GetFileInfoAll import start_db
from GetFileInfoAll import create_normalize_path


def summary_target_dir(db_dir, search_dir=None):
    """ summary target dir info

    :param db_dir: db dir path string
    :param search_dir: search dir path string
    :return: summary target dir info list
    """

    db_dict = start_db(db_dir)

    db = db_dict["db"]

    query = Query()

    def contain_file_summary(target):
        """ calculate contain dir file summary

        :param target: target dir path string
        :return: calculate dir info dict
        """

        file_dict = db.search((query.path.matches(target + ".*"))
                              & (query.path_type == "file"))

        file_list = [file["size"] for file in file_dict]

        return {"path": target,
                "files": len(file_list),
                "total_size": sum(file_list)}

    if search_dir is None:
        return contain_file_summary(db_dir)

    else:
        # check dir is contain database or not

        target_path_str = create_normalize_path(search_dir, slash=True)
        target_path = Path(target_path_str)

        level0_list = Path(db_dict["table_name"]).parts
        level0_str = "".join(level0_list)
        level0_len = len(level0_list)

        target_list = Path(target_path).parts
        target_len = len(target_list)
        reduce_len = level0_len if target_len > level0_len else target_len
        target_str = "".join(target_list[:reduce_len])

        if level0_str != target_str:
            return "not contains database"

        # check dir level
        target_level = target_len - level0_len

        dir_file_list = db.search((query.path.matches(target_path_str + ".*"))
                                  & (query.level == target_level + 1))

        # make summary of dir
        result_list = []

        for dir_file in tqdm(dir_file_list):

            if dir_file["path_type"] == "dir":
                result_list.append(contain_file_summary(dir_file["path"]))

            else:
                result_list.append({"files": 1,
                                    "path": dir_file["path"],
                                    "total_size": dir_file["size"]})

        return result_list


def error_search(db_dir):
    """ check error files

    :param db_dir: database path string
    :return: query result list
    """

    db_dict = start_db(db_dir)

    db = db_dict["db"]

    query = Query()

    error = db.search(query.path_type == "error")

    return error


def main():
    db_dir = "C:/"

    target_dir = "C:/"

    pprint(summary_target_dir(db_dir, target_dir))


if __name__ == "__main__":
    main()
