import numpy as np
import pandas as pd
from scipy import stats

class FactorProcessor:
    """
    因子处理框架，包含去极值、标准化、中性化等功能
    """
    def __init__(self, factor_data: pd.DataFrame, market_value: pd.DataFrame = None,
                 industry: pd.DataFrame = None):
        """
        初始化因子处理器
        
        参数:
            factor_data: 因子数据，DataFrame格式，索引为日期，列为股票代码
            market_value: 市值数据，DataFrame格式，索引为日期，列为股票代码
            industry: 行业数据，DataFrame格式，列为股票代码，值为行业代码
        """
        self.factor_data = factor_data.copy()
        self.market_value = market_value.copy() if market_value is not None else None
        self.industry = industry.copy() if industry is not None else None
        self.processed_factor = factor_data.copy()
    
    def winsorize(self, method: str = 'sigma', threshold: float = 3.0, 
                  percentile: tuple = (0.025, 0.975)) -> 'FactorProcessor':
        """
        去极值处理
        
        参数:
            method: 去极值方法，支持'sigma'(3 sigma),'percentile'(百分位法),'mad'(中位数绝对偏差法)
            threshold: sigma方法的阈值，默认为3.0
            percentile: 百分位法的分位数，默认为(0.025, 0.975)
        
        返回:
            处理后的FactorProcessor对象，支持链式调用
        """
        for date in self.processed_factor.index:
            factor_series = self.processed_factor.loc[date].dropna()
            
            if method == 'sigma':
                mean = factor_series.mean()
                std = factor_series.std()
                upper = mean + threshold * std
                lower = mean - threshold * std
            elif method == 'percentile':
                lower = factor_series.quantile(percentile[0])
                upper = factor_series.quantile(percentile[1])
            elif method == 'mad':
                median = factor_series.median()
                mad = np.median(np.abs(factor_series - median))
                upper = median + threshold * 1.4826 * mad
                lower = median - threshold * 1.4826 * mad
            else:
                raise ValueError(f"不支持的去极值方法: {method}")
            
            # 替换极端值
            self.processed_factor.loc[date] = factor_series.clip(lower, upper)
        
        return self
    
    def standardize(self, method: str = 'zscore', 
                   industry_neutral: bool = False) -> 'FactorProcessor':
        """
        标准化处理
        
        参数:
            method: 标准化方法，支持'zscore'(Z-score标准化),'minmax'(最小-最大标准化),'rank'(排名标准化)
            industry_neutral: 是否行业内标准化
        
        返回:
            处理后的FactorProcessor对象，支持链式调用
        """
        if industry_neutral and self.industry is None:
            raise ValueError("行业中性化需要提供行业数据")
        
        for date in self.processed_factor.index:
            factor_series = self.processed_factor.loc[date].dropna()
            
            if industry_neutral:
                industry = self.industry
                industry_groups = factor_series.groupby(industry)
                
                for industry, group in industry_groups:
                    if method == 'zscore':
                        standardized = (group - group.mean()) / (group.std() + 1e-8)
                    elif method == 'minmax':
                        standardized = (group - group.min()) / (group.max() - group.min() + 1e-8)
                    elif method == 'rank':
                        standardized = stats.rankdata(group) / len(group)
                    else:
                        raise ValueError(f"不支持的标准化方法: {method}")
                    
                    self.processed_factor.loc[date, group.index] = standardized
            else:
                if method == 'zscore':
                    standardized = (factor_series - factor_series.mean()) / (factor_series.std() + 1e-8)
                elif method == 'minmax':
                    standardized = (factor_series - factor_series.min()) / (factor_series.max() - factor_series.min() + 1e-8)
                elif method == 'rank':
                    standardized = stats.rankdata(factor_series) / len(factor_series)
                else:
                    raise ValueError(f"不支持的标准化方法: {method}")
                
                self.processed_factor.loc[date, factor_series.index] = standardized
        
        return self
    
    def neutralize(self, market_value_neutral: bool = True, 
                  industry_neutral: bool = True) -> 'FactorProcessor':
        """
        中性化处理（市值中性化和行业中性化）
        
        参数:
            market_value_neutral: 是否进行市值中性化
            industry_neutral: 是否进行行业中性化
        
        返回:
            处理后的FactorProcessor对象，支持链式调用
        """
        if (market_value_neutral and self.market_value is None) or \
           (industry_neutral and self.industry is None):
            raise ValueError("市值中性化需要市值数据，行业中性化需要行业数据")
        
        for date in self.processed_factor.index:
            factor_series = self.processed_factor.loc[date].dropna()
            stocks = factor_series.index
            
            # 准备自变量
            X = pd.DataFrame(index=stocks)
            
            if market_value_neutral:
                mv_series = self.market_value.loc[date, stocks]
                X['market_value'] = np.log(mv_series)  # 使用市值对数
            
            if industry_neutral:
                industry_series = self[stocks]
                industry_dummies = pd.get_dummies(industry_series, prefix='industry')
                X = pd.concat([X, industry_dummies], axis=1)
            
            # 处理缺失值
            X = X.fillna(0)
            
            # 确保有足够的样本进行回归
            if len(X) > X.shape[1] + 1:
                # 添加常数项
                X['intercept'] = 1
                
                # 多元线性回归
                try:
                    from statsmodels.api import OLS
                    model = OLS(factor_series, X).fit()
                    residuals = model.resid
                    self.processed_factor.loc[date, stocks] = residuals
                except:
                    # 如果无法进行回归，保留原始值
                    pass
        
        return self
    
    def get_processed_factor(self) -> pd.DataFrame:
        """获取处理后的因子数据"""
        return self.processed_factor

def process(factor_data,market_value,industry):
    """
        因子处理，去极值、标准化、行业市值中性化
        
        参数:
            factor_data: 因子数据，DataFrame格式，索引为日期，列为股票代码
            market_value: 市值数据，DataFrame格式，索引为日期，列为股票代码
            industry: 行业数据，DataFrame格式，列为股票代码，值为行业代码
    """
    # 初始化因子处理器
    processor = FactorProcessor(
        factor_data=factor_data,
        market_value=market_value,
        industry=industry
    )
        
    # 因子处理
    processed_factor = (
        processor
        .winsorize(method='mad', threshold=3.0)  # MAD去极值
        .standardize(method='zscore')            # Z-score标准化
        .neutralize(market_value_neutral=True, industry_neutral=True)  # 市值和行业中性化
        .get_processed_factor()
    )
        
    print("因子处理完成")
    print(f"处理后因子数据形状: {processed_factor.shape}")
    return processed_factor