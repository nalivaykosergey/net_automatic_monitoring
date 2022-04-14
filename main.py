#!/usr/bin/python3.8

import argparse
from model.CustomModel import CustomModel

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    h = "Файл конфигурации"
    parser.add_argument('-c', '--config', type=str, help=h)
    args = parser.parse_args()
    if args.config:
        top = CustomModel()
        top.configure_model(args.config)
        top.simulation()
    else:
        print("Введите название конфиг-файла")
