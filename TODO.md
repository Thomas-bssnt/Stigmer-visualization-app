# TODO

## Important changes

- [ ] Change `lbl_info` to a “table” 

## Future options
- [ ] Show/hide values on the map
- [ ] Change play speed
- [ ] Show instantaneous/cumulate proportions
- [ ] Work with other size of map:
    - [ ] Adapt the size to the `in_data["mapSize"]` which is unknown  at the beginning
    - [ ] Remove the following code in the `__init__` of the class `MainApplication`
        ```python
            file_name = 'S01-A1-R1-MR-01'
            path_in_file = path_data + f'Session_{file_name[1:3]}/In/{file_name}.json'
            with open(path_in_file) as in_file:
                self.in_data = json.load(in_file)
        ```
