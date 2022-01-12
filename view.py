from tkinter import Tk, Button, Label, PhotoImage, Frame, ttk, simpledialog, Toplevel, Entry, filedialog, Text, END
from tkcalendar import DateEntry
from pprint import pprint

from control import get_data, load_tickers, save_as_tickers, smartlab_import

class View:

	def __init__(self, root):
		self.info = None
		self.master = root

		# Toolbar
		shortcut_bar = Frame(self.master, height=25)
		shortcut_bar.pack(expand='no', fill='x')

		# Toolbar icons
		icons = ('openfile', 'save_as_file', 'import', )
		for i, icon in enumerate(icons):
			tool_bar_icon = PhotoImage(file=f'icons/tb_{icon}.png').subsample(x=16, y=16)
			tool_bar = Button(shortcut_bar, image=tool_bar_icon, command=eval(f'self.cmd_{icon}'))
			tool_bar.image = tool_bar_icon
			tool_bar.pack(side='left')

		# Frame control (calendar)
		self.frame_control = Frame(self.master, relief='sunken', borderwidth = 1, height=50)
		Label(self.frame_control, text='Дата: ', font=('Arial', 14)).grid(row=0, column=0)
		self.cal = DateEntry(self.frame_control, selectmode='day', date_pattern='y-mm-dd')
		self.cal.grid(row=0, column=1)
		self.cal.bind('<<DateEntrySelected>>', lambda e: self.run())
		self.frame_control.pack(expand='no', fill='x')


		self.headers = ('title', 'ticker', 'count', 'price', 'sum', 'part')
		self.headers_ = ('Наименование', 'Тикер', 'Количество', 'Цена', 'Сумма', 'Доля')

		self.frame_content = Frame(self.master)
		self.content = ttk.Treeview(self.frame_content, 
								columns=self.headers,
								show='headings'
							)
		for i, header in enumerate(self.headers):
			self.content.heading(header, text=self.headers_[i])

		self.content.tag_configure('red', background='red')

		self.content.pack(fill='both', expand=True)
		self.frame_content.pack(fill='both', expand=True)
		
		# Display tickers and counts
		self.tickers = load_tickers('tickers.csv')
		if self.tickers:
			self.show_tickers()

	def show_tickers(self):
		self.content.delete(*self.content.get_children())
		for ticker in self.tickers:
			self.content.insert('', 'end', values=ticker)
				


	def run(self):
		# retrieve data from site
		self.info = get_data(self.cal.get_date(), self.tickers)
		
		# clear content
		self.content.delete(*self.content.get_children())

		# display data
		for row, (k, v) in enumerate(sorted(self.info.items(), key=lambda x: x[1]['part'], reverse=True), start=1):
			if v['part'] > 10:
				self.content.insert('', 'end', values=(v['title'], k, v['count'], v['price'], v['sum'], v['part']), tags=('red'))
			else:
				self.content.insert('', 'end', values=(v['title'], k, v['count'], v['price'], v['sum'], v['part']))

		# results
		self.results = round(sum([s['sum'] for s in self.info.values()]), 2)
		self.content.insert('', 'end', values=('Итого: ', '', '', '', '', self.results))		


	def cmd_import(self):
		def import_(url):
			try:
				self.tickers = smartlab_import(url)
				self.show_tickers()
			finally:
				import_toplevel.destroy()

		import_toplevel = Toplevel(self.master)
		import_toplevel.title('Импорт со Смартлаба')
		import_toplevel.transient(self.master)
		import_toplevel.resizable(0,0) 
		Label(import_toplevel, text='URL: ').grid(row=0, column=0, sticky='e')
		import_entry = Entry(import_toplevel, width=55)
		import_entry.grid(row=0, column=1, padx=2, pady=2, sticky='we')
		import_entry.focus_set()
		Button(import_toplevel, text='OK', command=lambda: import_(import_entry.get())).grid(row=0, column=2, sticky='ew', padx=2, pady=2)

	def cmd_openfile(self):
		filename = filedialog.askopenfilename(defaultextension='*.csv', multiple=False, filetypes=[('CSV documents', '*.csv')])
		if filename:
			self.tickers = load_tickers(filename)
			self.show_tickers()

	def cmd_save_as_file(self):
		filename = filedialog.asksaveasfilename(defaultextension='*.csv', filetypes=[('CSV documents', '*.csv'), ('HTML documents', '*.html')])
		if filename:
			save_as_tickers(filename, self.info)

def main():
	root = Tk()
	root.title('Получение котировок с Мосбиржи')
	icon = PhotoImage(file = 'icons/mmvb.png')
	root.iconphoto(False, icon)
	root.geometry('1024x768')
	view = View(root)
	root.mainloop()

if __name__ == '__main__':
	main()