# mscthesis

## Setup Original Datasets

The original datasets are located in the [data](data) directory. They are registered as git submodules.

To retrieve them, you must init and update them:
```bash
git submodule init
git submodule update
```

### Defects4J

To setup Defects4J, follow the instructions under [data/defects4j/README.md#setting-up-defects4j](data/defects4j/README.md#setting-up-defects4j)

Under [src/data/defects4j](src/data/defects4j) you can find a script for checking out all Defects4J bugs and a script for checking their integrity.

```bash
python src/data/defects4j/checkout_all.py --storage ./storage/defects4j --defects4j ./date/defects4j
python src/data/defects4j/check_integrity.py --storage ./storage/defects4j --defects4j ./date/defects4j
```

### Bugs.jar

To setup Bugs.jar, follow the instructions under [data/bugs-dot-jat/README.md#directory--file-structure](data/bugs-dot-jat/README.md#directory--file-structure)
