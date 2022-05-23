from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.data_file_io.data_file_stream_processor import DataFileStreamProcessor
from openmsipython.osn.s3_data_transfer import s3_data_transfer
from openmsipython.pdv.config import LECROY_CONST
from openmsipython.pdv.lecroy_data_file import DownloadLecroyDataFile
from openmsipython.shared.runnable import Runnable
import logging

class osn_stream_processor(DataFileStreamProcessor, Runnable):

    @property
    def other_datafile_kwargs(self):
        return {'header_rows': self.__header_rows}

    def __init__(self, bucket_name, config_path, topic_name,
                 header_rows=LECROY_CONST.HEADER_ROWS, **otherkwargs):

        super().__init__(config_path, topic_name, datafile_type=DownloadLecroyDataFile, **otherkwargs)

        self.__header_rows = header_rows
        self.__osn_config = super().get_osn_config()
        self.__osn_config['bucket_name'] = bucket_name
        self.bucket_name = bucket_name
        self.s3d = s3_data_transfer(self.__osn_config)

    def make_stream(self):
        _, _, processed_data_filepaths = self.process_files_as_read()

        return self.n_msgs_read

    def _process_downloaded_data_file(self, datafile, lock):

        self.s3d.transfer_object_stream(self.topic_name, datafile)

        if self.s3d.compare_consumer_datafile_with_osn_object_stream(self.topic_name, self.bucket_name, datafile):
            file_name = str(datafile.filename)
            sub_dir = datafile.get_subdir_str
            object_key = sub_dir + '/' + file_name
            logging.info(object_key + ' matched with consumer datafile')
            # self.s3d.delete_object_from_osn(self.bucket_name, object_key)
        return None

    @classmethod
    def get_command_line_arguments(cls):
        superargs, superkwargs = super().get_command_line_arguments()
        args = [*superargs, 'bucket_name',
                'update_seconds', 'logger_file']
        kwargs = {**superkwargs,
                  'config': RUN_OPT_CONST.PRODUCTION_CONFIG_FILE,
                  'topic_name': LECROY_CONST.TOPIC_NAME,
                  'n_threads': RUN_OPT_CONST.N_DEFAULT_DOWNLOAD_THREADS
            , 'consumer_group_ID': 'osn_data_consumer'}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        """

        """
        # make the argument parser
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)

        osn_stream_proc = cls(
            args.bucket_name,
            args.config, args.topic_name,
            n_threads=args.n_threads,
            update_secs=args.update_seconds,
            consumer_group_ID=args.consumer_group_ID,
            logger_file=args.logger_file)

        # cls.bucket_name = args.bucket_name
        msg = f'Listening to the {args.topic_name} topic to find Lecroy data files and create '
        osn_stream_proc.logger.info(msg)
        # n_read, n_processed = osn_stream_proc.make_stream()
        n_read, n_processed = osn_stream_proc.make_stream()
        osn_stream_proc.close()
        # run_stop = datetime.datetime.now()
        # shut down when that function returns
        msg = ''
        if args.output_dir is not None:
            msg += f'writing to {args.output_dir} '
        msg += 'shut down'
        osn_stream_proc.logger.info(msg)
        msg = f'{n_read} total messages were consumed'
        osn_stream_proc.logger.info(msg)


#################### MAIN METHOD TO RUN FROM COMMAND LINE ####################

def main(args=None):
    osn_stream_processor.run_from_command_line(args)


if __name__ == '__main__':
    main()
