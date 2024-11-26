def main():
    fun(a='a',b='b',c='c')

def fun(*args, **kwargs):
    print(args, kwargs, sep='\n')
    print(kwargs['a'])

if __name__ == '__main__':
    main()