# Factor Mining for A Share （I）

MFE5210 Algorithm Trading 24/25

This will include:  
a. Code for generating alpha factors
b. Reference
c. Readme

- i. Correlation matrix (maximal correlation is 0.5)

- ii. Average sharp ratio for all alpha factors (without cost)

- iii. others  

## Data

Tushare: <https://tushare.pro/document/1?doc_id=131>

Token(5000 points):

```PlainText
2876ea85cb005fb5fa17c809a98174f2d5aae8b1f830110a5ead6211
```
see [get_date.ipynb](get_data.ipynb)

## Reference
[Alphalens](https://github.com/quantopian/alphalens.git) [指南](https://zhuanlan.zhihu.com/p/256324663)

[中金-价量因子手册](references\中金-量化多因子手册\中金公司-量化多因子系列（7）：价量因子手册-56页.pdf)

[量价背离因子](https://bigquant.com/wiki/doc/Hn333yYkfS)

[全换手天数因子](https://www.joinquant.com/view/community/detail/71d8b77cbd1da76b659e04d2c7478c0c?type=1)

[下轨线（布林线）指标 boll_down](https://www.joinquant.com/view/factorlib/detail/94aec050cf469a9803395b8994f5e5ac?buildtype=0&universetype=eno1MDA%3D&period=M3k%3D&commisionFee=MA%3D%3D&skipPaused=MQ%3D%3D)