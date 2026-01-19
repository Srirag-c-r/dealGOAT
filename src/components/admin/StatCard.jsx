import React from 'react';

const StatCard = ({ title, value, change, icon: Icon, color = 'blue', trend = 'up' }) => {
    const colorClasses = {
        blue: 'bg-blue-500',
        green: 'bg-green-500',
        red: 'bg-red-500',
        yellow: 'bg-yellow-500',
        purple: 'bg-purple-500',
        indigo: 'bg-indigo-500',
    };

    const trendColor = trend === 'up' ? 'text-green-600' : 'text-red-600';

    return (
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
            <div className="flex items-center justify-between">
                <div className="flex-1">
                    <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">
                        {title}
                    </p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                        {value}
                    </p>
                    {change !== undefined && (
                        <p className={`text-sm mt-2 ${trendColor} font-medium`}>
                            {trend === 'up' ? '↑' : '↓'} {Math.abs(change)}% from last period
                        </p>
                    )}
                </div>
                <div className={`${colorClasses[color]} p-4 rounded-lg`}>
                    <Icon className="w-8 h-8 text-white" />
                </div>
            </div>
        </div>
    );
};

export default StatCard;
