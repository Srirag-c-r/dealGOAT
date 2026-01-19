import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const CustomBarChart = ({ data, bars, xKey = 'name', height = 300, title, horizontal = false }) => {
    const colors = ['#DC2626', '#10B981', '#3B82F6', '#F59E0B', '#8B5CF6'];

    const ChartComponent = horizontal ? BarChart : BarChart;
    const layout = horizontal ? 'horizontal' : 'vertical';

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            {title && <h3 className="text-lg font-bold text-gray-900 mb-4">{title}</h3>}
            <ResponsiveContainer width="100%" height={height}>
                <ChartComponent data={data} layout={layout}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    {horizontal ? (
                        <>
                            <XAxis type="number" stroke="#6B7280" style={{ fontSize: '12px' }} />
                            <YAxis dataKey={xKey} type="category" stroke="#6B7280" style={{ fontSize: '12px' }} />
                        </>
                    ) : (
                        <>
                            <XAxis dataKey={xKey} stroke="#6B7280" style={{ fontSize: '12px' }} />
                            <YAxis stroke="#6B7280" style={{ fontSize: '12px' }} />
                        </>
                    )}
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1F2937',
                            border: 'none',
                            borderRadius: '8px',
                            color: '#fff'
                        }}
                    />
                    <Legend />
                    {bars.map((bar, index) => (
                        <Bar
                            key={bar.dataKey}
                            dataKey={bar.dataKey}
                            fill={bar.color || colors[index % colors.length]}
                            name={bar.name}
                            radius={[4, 4, 0, 0]}
                        />
                    ))}
                </ChartComponent>
            </ResponsiveContainer>
        </div>
    );
};

export default CustomBarChart;
