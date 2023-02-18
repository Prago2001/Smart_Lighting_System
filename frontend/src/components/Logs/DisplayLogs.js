import React, { useState,useEffect } from "react";
import Pagination from '@mui/material/Pagination';
import usePagination from "./Pagination";
import axios from "axios";
import url from "../BaseURL";
import Stack from '@mui/material/Stack';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Skeleton from '@mui/material/Skeleton';

export default function DisplayLogs(){
    const [data,setData] = useState([]);
    let [page, setPage] = useState(1);
    const [loading,setLoading] = useState(false);
    const PER_PAGE = 10;

    const count = Math.ceil(data.length/ PER_PAGE);
    const _DATA = usePagination(data, PER_PAGE);

    const handleChange = (e, p) => {
        setPage(p);
        _DATA.jump(p);
    };
    useEffect(() => {
        setLoading(true);
        axios.get(url + "logs/").then((res) => {
            setData(res.data.logs);
            setLoading(false);
        });
    }, []);

    return (
        <div>
            <Pagination
                count={count}
                size="large"
                page={page}
                color='primary'
                onChange={handleChange}
                sx={{
                    m:2,
                    p:2,
                    ml:-2,
                    pl:-2,
                    mt:-1
                }}
            />
            <Stack spacing={1}>
                {loading ? (
                    <div>
                        <Skeleton 
                            variant="rounded"
                            animation="wave"
                            height='20%'

                        />
                        <Skeleton 
                            variant="rounded"
                            animation="wave"
                            height='20%'

                        />
                    </div>
                    
                
                ) : (
                
                    _DATA.currentData().map((record) => {
                        const date = new Date(record.timestamp);
                        const day = date.toLocaleString('en-IN',{day:'2-digit'});
                        const month = date.toLocaleString('en-IN',{month:"short"});
                        const year = date.getFullYear();
                        const time = date.toLocaleString('en-IN',{hour:"2-digit",minute:"2-digit"});
                        const min = date.getMinutes();
                        return (
                        <Alert 
                            severity={record.success ? "success" : "error"}
                            sx={{
                                fontSize:19,
                                fontWeight: 'medium'
                            }}
                        >
                            <AlertTitle
                                sx={{
                                    fontSize:21
                                }}
                            >
                                <strong>{record.message}</strong>
                            </AlertTitle>
                            {day}-{month}-{year} {time}
                        </Alert>
                        )
                    })
                )}
            </Stack>

        </div>
    )
}
