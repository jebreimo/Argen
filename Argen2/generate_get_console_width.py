# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-08-11.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def generate_include_files():
    return include_text.split("\n")


def generate_get_console_width():
    return code_text.split("\n")


include_text = """\
#if defined(__APPLE__) || defined(unix) || defined(__unix) || defined(__unix__)
    #include <sys/ioctl.h>
    #include <unistd.h>
#elif defined(WIN32)
    #include <Windows.h>
#endif"""


code_text = """\
#if defined(__APPLE__) || defined(unix) || defined(__unix) || defined(__unix__)

int get_console_width()
{
    winsize ws = {};
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == -1)
        return 0;
    return ws.ws_col;
}

#elif defined(WIN32)

int get_console_width()
{
  HANDLE hCon = GetStdHandle(STD_OUTPUT_HANDLE);
  if (hCon == INVALID_HANDLE_VALUE)
    return 0;

  CONSOLE_SCREEN_BUFFER_INFO conInfo;
  if (!GetConsoleScreenBufferInfo(hCon, &conInfo))
    return 0;

  return conInfo.srWindow.Right - conInfo.srWindow.Left + 1;
}

#else

constexpr int get_console_width()
{
    return 80;
}

#endif
"""