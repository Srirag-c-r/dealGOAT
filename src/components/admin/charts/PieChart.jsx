import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const CustomPieChart = ({ data, dataKey = 'value', nameKey = 'name', height = 300, title, showLabels = true }) => {
    const COLORS = ['#DC2626', '#10B981', '#3B82F6', '#F59E0B', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'];

    const renderLabel = (entry) => {
        if (!showLabels) return null;
        return `${entry[nameKey]}: ${entry[dataKey]}`;
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            {title && <h3 className="text-lg font-bold text-gray-900 mb-4">{title}</h3>}
            <ResponsiveContainer width="100%" height={height}>
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        labelLine={showLabels}
                        label={showLabels ? renderLabel : false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey={dataKey}
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1F2937',
                            border: 'none',
                            borderRadius: '8px',
                            color: '#fff'
                        }}
                    />
                    <Legend />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};

export default CustomPieChart;
