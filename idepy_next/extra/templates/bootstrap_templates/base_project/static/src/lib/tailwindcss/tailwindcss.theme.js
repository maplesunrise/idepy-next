tailwind.config = {
  theme: {
    extend: {
        colors: {
                        // 添加自定义颜色
                        primary: {
                            DEFAULT: "var(--el-color-primary)",
                            "light-3": "var(--el-color-primary-light-3)",
                            "light-5": "var(--el-color-primary-light-5)",

                            "light-7": "var(--el-color-primary-light-7)",
                            "light-8": "var(--el-color-primary-light-8)",
                            "light-9": "var(--el-color-primary-light-9)",
                            "dark-2": "var(--el-color-primary-dark-2)",
                        },
                        success: {
                            DEFAULT: "var(--el-color-success)",
                            "light-3": "var(--el-color-success-light-3)",
                            "light-5": "var(--el-color-success-light-5)",

                            "light-7": "var(--el-color-success-light-7)",
                            "light-8": "var(--el-color-success-light-8)",
                            "light-9": "var(--el-color-success-light-9)",
                            "dark-2": "var(--el-color-success-dark-2)",
                        },
                        danger: {
                            DEFAULT: "var(--el-color-danger)",
                            "light-3": "var(--el-color-danger-light-3)",
                            "light-5": "var(--el-color-danger-light-5)",

                            "light-7": "var(--el-color-danger-light-7)",
                            "light-8": "var(--el-color-danger-light-8)",
                            "light-9": "var(--el-color-danger-light-9)",
                            "dark-2": "var(--el-color-danger-dark-2)",
                        },
                        warning: {
                            DEFAULT: "var(--el-color-warning)",
                            "light-3": "var(--el-color-warning-light-3)",
                            "light-5": "var(--el-color-warning-light-5)",

                            "light-7": "var(--el-color-warning-light-7)",
                            "light-8": "var(--el-color-warning-light-8)",
                            "light-9": "var(--el-color-warning-light-9)",
                            "dark-2": "var(--el-color-warning-dark-2)",
                        },
                        info: {
                            DEFAULT: "var(--el-color-info)",
                            "light-3": "var(--el-color-info-light-3)",
                            "light-5": "var(--el-color-info-light-5)",

                            "light-7": "var(--el-color-info-light-7)",
                            "light-8": "var(--el-color-info-light-8)",
                            "light-9": "var(--el-color-info-light-9)",
                            "dark-2": "var(--el-color-info-dark-2)",
                        },
                        black: {
                            DEFAULT: "#000",
                            primary: "#303133",
                            regular: "#606266",
                            secondary: "#909399",
                            placeholder: "#A8ABB2",
                            disabled: "#C0C4CC",
                        },
                        shop: "#FF5000",

                        // 删除默认颜色
                        neutral: [],
                        stone: [],
                        slate: [],
                        zinc: [],
                        red: [],
                        orange: [],
                        amber: [],
                        yellow: [],
                        lime: [],
                        green: [],
                        emerald: [],
                        teal: [],
                        cyan: [],
                        sky: [],
                        blue: [],
                        indigo: [],
                        violet: [],
                        purple: [],
                        fuchsia: [],
                        pink: [],
                        rose: [],


                    }
    },
  }
}