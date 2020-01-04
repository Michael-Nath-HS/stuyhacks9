from curses import wrapper
import curses
import time

def center_height(stdscr, height):
    window_height, window_length = stdscr.getmaxyx()
    center_height = window_height / 2
    return int(center_height - height / 2)

def center_length(stdscr, length):
    window_height, window_length = stdscr.getmaxyx()
    center_length = window_length / 2
    return int(center_length - length / 2)

def center_window(stdscr, height, length):
    window_height, window_length = stdscr.getmaxyx()
    center_height = window_height / 2
    center_length = window_length / 2
    return curses.newwin(height, length, center_height(height), center_length(length))
   #return curses.newwin(height, length, int(center_height), int(center_length))

def menu(stdscr):
    window_height, window_length = stdscr.getmaxyx()
    titlewin = curses.newwin(5, 24, center_height(stdscr, 5) - 15, center_length(stdscr, 24))
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
    titlewin.addstr(1, 1, "🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒", curses.color_pair(3))
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    titlewin.addstr(2, 1, "      SecurEvent      ", curses.color_pair(2))
    titlewin.addstr(3, 1, "🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒", curses.color_pair(3))
    titlewin.box()
    titlewin.refresh()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    choiceswin = curses.newwin(8, 60, center_height(stdscr, 8), center_length(stdscr, 60))
    choiceswin.box()
    choiceswin.bkgd(' ', curses.color_pair(1))
    choiceswin.addstr(1, 2, "📋 Press 'S' to sign-up to SecurEvent")
    choiceswin.addstr(2, 2, "🔑 Press 'L' to login to SecurEvent")
    choiceswin.addstr(3, 2, "✏️ Press 'C' to create a SecurEvent")
    choiceswin.addstr(4, 2, "🔍 Press 'V' to view a SecurEvent with its ID")
    choiceswin.addstr(5, 2, "✉️ Press 'I' to invite someone to your SecurEvent")
    choiceswin.addstr(6, 2, "👍 Press 'R' to respond to an invite to a SecurEvent")
    choiceswin.refresh()

def main(stdscr):
    menu(stdscr)
    time.sleep(10)
wrapper(main)