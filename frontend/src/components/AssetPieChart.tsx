import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { AssetTrend } from '../api/client';
import { VIVID_PALETTE } from '../utils/constants';

interface AssetPieChartProps {
  data: AssetTrend[];
}

const AssetPieChart: React.FC<AssetPieChartProps> = ({ data }) => {
  const pieData = useMemo(() => {
    if (!data.length) return [];
    
    // 最新の日付を特定
    const latestDate = data.reduce((max, item) => 
      item.acquired_date > max ? item.acquired_date : max, 
      data[0].acquired_date
    );

    // 最新日付のデータを抽出
    return data
      .filter(item => item.acquired_date === latestDate)
      .map(item => ({
        name: item.asset_type,
        value: item.total_amount
      }))
      .filter(item => item.value > 0);
  }, [data]);

  if (pieData.length === 0) {
    return <div className="text-slate-400 text-xs text-center p-8">データがありません</div>;
  }

  return (
    <div className="w-full h-full min-h-[200px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
            label={{ fill: '#fff', fontSize: 10, fontWeight: 'bold' }}
          >
            {pieData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={VIVID_PALETTE[index % VIVID_PALETTE.length]} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#0f172a', 
              border: '1px solid #1e293b', 
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              color: '#f1f5f9'
            }}
            itemStyle={{ color: '#f1f5f9' }}
            formatter={(value: any) => [`¥${Number(value).toLocaleString()}`, '金額']}
          />
          <Legend 
            verticalAlign="bottom" 
            align="center" 
            iconType="circle" 
            wrapperStyle={{ fontSize: '10px', fontWeight: 'bold', paddingTop: '10px', color: '#fff' }} 
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AssetPieChart;
