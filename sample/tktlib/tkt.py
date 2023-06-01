# https://github.com/kihiyuki/tkinter-template
# Copyright (c) 2023 kihiyuki
# Released under the MIT license
# Supported Python versions: 3.8
# Requires: (using only Python Standard Library)
from typing import Optional, Union, Dict, Any
from pathlib import Path
from tkinter import (
    Tk,
    ttk,
    Toplevel,
    Variable,
    StringVar,
    Entry,
    filedialog,
    W,
    END,
)


FONTSIZE = 12
SCALE = 1.5
class LabelKw(dict):
    def __init__(self, fontsize: int = FONTSIZE):
        return super().__init__(
            font = ("", fontsize),
        )

    def specify_scale(self, scale: float) -> dict:
        _d = self.copy()
        _d["font"] = ("", int(_d["font"][1] * scale))
        return _d

    @property
    def big(self) -> dict:
        return self.specify_scale(SCALE)

    @property
    def small(self) -> dict:
        return self.specify_scale(1 / SCALE)


class GridKw(object):
    def __init__(self, maxcolumn: Optional[int] = None, sticky: str = W) -> None:
        self.row: int = 0
        self.column: int = 0
        self.columnspan: int = 1
        self.maxcolumn: Optional[int] = maxcolumn
        self.sticky: str = sticky
        return None

    def lf(self, n: int = 1) -> None:
        """Line feed"""
        self.row += n
        self.column = 0
        return None

    def next(self) -> None:
        self.column += 1
        if self.maxcolumn is None:
            pass
        elif self.column >= self.maxcolumn:
            self.lf()
        return None

    def set(self, row: Optional[int] = None, column: Optional[int] = None) -> None:
        if row is not None:
            self.row = row
        if column is not None:
            self.column = column
        return None

    def pull(self, fullspan: bool = False) -> dict:
        row = self.row
        column = self.column
        sticky = self.sticky
        columnspan = self.columnspan
        if fullspan:
            columnspan = self.maxcolumn
            self.lf()
        else:
            self.next()
        return dict(
            row = row,
            column = column,
            columnspan = columnspan,
            sticky = sticky,
        )


class _DictLikeObjects(object):
    def __init__(
        self,
        datatype,
        keys: Union[list, tuple, set, None] = None,
        defaltvalue: Optional[str] = None,
        **kwargs,
    ) -> None:
        self._datatype = datatype
        self._data: Dict[Any, self._datatype] = {}
        self._defaultvalue: Optional[str] = defaltvalue
        if keys is not None:
            for k in keys:
                self.add(k, **kwargs)
        return None

    def add(self, key: Any, defaltvalue: Optional[str] = None, **kwargs) -> None:
        if key in self._data.keys():
            raise KeyError(f"Key '{key}' already exists")
        self._data[key] = self._datatype(**kwargs)
        if defaltvalue is None:
            defaltvalue = self._defaultvalue
        if defaltvalue is None:
            self._data[key].set(key)
        else:
            self._data[key].set(defaltvalue)
        return None

    def get_instance(self, key: Any):
        return self._data[key]

    def get(self, key: Any) -> str:
        return self._data[key].get()

    def set(self, key: Any, value: str) -> None:
        return self._data[key].set(value)

    def __getitem__(self, key: Any):
        return self.get(key=key)

    def __setitem__(self, key: Any, value: str):
        return self.set(key=key, value=value)

    def items(self):
        return self._data.items()

class StringVars(_DictLikeObjects):
    def __init__(
        self,
        keys: Union[list, tuple, set, None] = None,
        defaltvalue: Optional[str] = None,
        **kwargs,
    ) -> None:
        self._data: Dict[Any, StringVar]
        return super().__init__(StringVar, keys=keys, defaltvalue=defaltvalue, **kwargs)


class SettableEntry(Entry):
    def set(self, value: str) -> None:
        self.delete(0, END)
        self.insert(END, value)
        return None


class Entries(_DictLikeObjects):
    def __init__(
        self,
        keys: Union[list, tuple, set, None] = None,
        defaltvalue: Optional[str] = None,
        **kwargs,
    ) -> None:
        self._data: Dict[Any, SettableEntry]
        return super().__init__(SettableEntry, keys=keys, defaltvalue=defaltvalue, **kwargs)


class GridObject(object):
    def __init__(self, frame: ttk.Frame) -> None:
        self._data: Dict[str, ttk.Widget] = dict()
        self.frame: ttk.Frame = frame
        return None

    def add(
        self,
        __object,
        gridkw: GridKw,
        text: Optional[str] = None,
        name: Optional[str] = None,
        fullspan: bool = False,
    ) -> None:
        if name is None:
            name = text
        if name in self._data:
            raise ValueError(f"Name '{name}' is always used")
        self._data[name] = __object
        return self._data[name].grid(**gridkw.pull(fullspan=fullspan))


class Labels(GridObject):
    def add(
        self,
        text: Any,
        labelkw: LabelKw,
        gridkw: GridKw,
        name: Optional[str] = None,
        fullspan: bool = False,
    ) -> None:
        if type(text) is str:
            _obj = ttk.Label(self.frame, text=text, **labelkw)
        else:
            _obj = ttk.Label(self.frame, textvariable=text, **labelkw)
        return super().add(_obj, gridkw, text=text, name=name, fullspan=fullspan)


class Buttons(GridObject):
    def add(
        self,
        text: str,
        command,
        gridkw: GridKw,
        name: Optional[str] = None,
        fullspan: bool = False,
    ) -> None:
        _obj = ttk.Button(self.frame, text=text, command=command)
        return super().add(_obj, gridkw, text=text, name=name, fullspan=fullspan)


class RadioButtons(GridObject):
    def add(
            self,
            text: str,
            value: Any,
            variable: Variable,
            gridkw: GridKw,
            name: str = None,
            fullspan: bool = False,
        ) -> None:
        _obj = ttk.Radiobutton(self.frame, text=text, variable=variable, value=value)
        return super().add(_obj, gridkw, text=text, name=name, fullspan=fullspan)


class RootWindow(Tk):
    def __init__(self, maxcolumn: int = 4, padding: int = 20, **kwargs) -> None:
        _ret = super().__init__(**kwargs)
        self.frame = ttk.Frame(self, padding=padding)
        self.frame.grid()

        self.gridkw = GridKw(maxcolumn=maxcolumn)
        self.labelkw = LabelKw()

        self.buttons = Buttons(self.frame)
        self.labels = Labels(self.frame)
        self.stringvars = StringVars([], defaltvalue="")

        return _ret

    def close(self, event=None):
        self.destroy()

class SubWindow(Toplevel):
    def __init__(
        self,
        title: str,
        resizable: bool = False,
        padding: int = 20,
        maxcolumn: int = 1,
        sticky: str = W,
        fontsize: int = FONTSIZE,
        button: bool = False,
        label: bool = False,
        radiobutton: bool = False,
    ) -> None:
        _ret = super().__init__()

        self.title(title)
        self.resizable(resizable, resizable)
        self.grab_set()
        self.focus_set()

        self.frame = ttk.Frame(self, padding=padding)
        self.frame.grid()

        self.gridkw = GridKw(maxcolumn=maxcolumn, sticky=sticky)
        self.labelkw = LabelKw(fontsize=fontsize)

        if button:
            self.buttons = Buttons(self.frame)
        if label:
            self.labels = Labels(self.frame)
        if radiobutton:
            self.radiobuttons = RadioButtons(self.frame)

        return _ret

    def close(self, event=None) -> None:
        self.grab_release()
        self.destroy()
        return None


class dialog(object):
    @staticmethod
    def askopenpath(
        initialpath: Union[str, Path],
        mode: str = "f",
        returntype: str = "str",
    ) -> Union[str, Path, None]:
        """askopenfilename/askdirectory

        Args:
            mode: 'f'=file, 'd'=dir
            returntype: 'str', 'Path'
        """
        initialpath = Path(initialpath).resolve()
        if initialpath.is_dir():
            dirpath = str(initialpath)
            filename = None
        elif initialpath.parent.is_dir():
            dirpath = str(initialpath.parent)
            filename = str(initialpath.name)
        else:
            dirpath = None
            filename = None

        mode = mode.lower()
        if mode in {"f", "file"}:
            selectedpath = filedialog.askopenfilename(
                title="Choose a file",
                initialfile=filename,
                initialdir=dirpath,
            )
        elif mode in {"d", "dir", "directory"}:
            selectedpath = filedialog.askdirectory(
                title="Choose a directory",
                initialdir=dirpath,
            )
        else:
            raise ValueError(f"Invalid mode: '{mode}'")
        if len(selectedpath) > 0:
            if returntype == "str":
                return selectedpath
            elif returntype == "Path":
                return Path(selectedpath)
            else:
                raise ValueError(f"Invalid returntype: '{returntype}'")
        else:
            return None
